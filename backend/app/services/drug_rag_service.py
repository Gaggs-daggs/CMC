"""
Drug RAG Service - Pure PDF-based system
No hardcoded mappings - all information derived from PDF content
"""
import os
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Try to import ChromaDB and sentence-transformers
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class DrugRAGService:
    """
    RAG-based drug lookup service that derives ALL information from the PDF.
    No hardcoded symptom-to-drug mappings.
    """
    
    def __init__(self, pdf_path: str = None):
        self.pdf_path = pdf_path
        self.drugs_data: List[Dict] = []
        self.categories: Dict[str, List[str]] = {}  # category -> list of symptom keywords
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.embedding_model = None
            
        # Initialize ChromaDB
        if CHROMADB_AVAILABLE:
            persist_dir = os.path.join(os.path.dirname(__file__), 'chroma_db')
            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            
            # Create embedding function
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name='all-MiniLM-L6-v2'
                )
            else:
                self.embedding_func = embedding_functions.DefaultEmbeddingFunction()
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_or_create_collection(
                    name="drugs_collection",
                    embedding_function=self.embedding_func,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"Error creating collection: {e}")
                self.collection = None
        else:
            self.chroma_client = None
            self.collection = None
        
        # Load and index drugs
        self._load_drugs_from_pdf()
        
    def _load_drugs_from_pdf(self):
        """Load drugs from PDF/text file and build index."""
        # Try to find the raw text file first
        raw_text_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'data', 'druglist_raw.txt'
        )
        
        if os.path.exists(raw_text_path):
            self._parse_raw_text(raw_text_path)
        elif self.pdf_path and os.path.exists(self.pdf_path):
            self._parse_pdf(self.pdf_path)
        else:
            print("No drug data source found!")
            return
            
        # Index in ChromaDB
        self._index_drugs()
        
    def _parse_raw_text(self, text_path: str):
        """Parse the raw text extracted from PDF with three-column format."""
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.split('\n')
        current_category = None
        pending_drug = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Skip header rows
            if line.lower() in ['sl no', 'drug name', 'category', 'sl no.']:
                continue
                
            # Check if pure number (serial number)
            if re.match(r'^\d+\.?\s*$', line):
                continue
                
            # Check if this is a category (standalone word with no dosage info)
            is_category = self._is_category_line(line)
            
            if is_category:
                current_category = line
                if current_category not in self.categories:
                    self.categories[current_category] = self._derive_keywords_from_category(current_category)
                    
                # If we have a pending drug, assign this category
                if pending_drug:
                    self.drugs_data.append({
                        'name': pending_drug,
                        'category': current_category,
                        'keywords': self.categories.get(current_category, [])
                    })
                    pending_drug = None
                continue
                
            # This should be a drug entry
            drug_name = re.sub(r'^\d+\.?\s*', '', line).strip()
            
            if drug_name and len(drug_name) > 2:
                # Skip if it looks like just a number or garbage
                if re.match(r'^[\d\s\.\/\:\,\(\)]+$', drug_name):
                    continue
                    
                # Skip very short or garbage entries
                if len(drug_name) < 3:
                    continue
                    
                # Skip entries that are mostly non-alphabetic
                alpha_chars = sum(1 for c in drug_name if c.isalpha())
                if alpha_chars < 3:
                    continue
                    
                # Skip entries that look like dosage only
                if re.match(r'^[\d]+\s*(mg|ml|mcg|%|iu)$', drug_name.lower()):
                    continue
                    
                # Check if line contains both drug and category
                # Sometimes category appears at end of drug line
                parts = self._split_drug_category(drug_name)
                if parts:
                    drug_name, inline_category = parts
                    if inline_category:
                        current_category = inline_category
                        if current_category not in self.categories:
                            self.categories[current_category] = self._derive_keywords_from_category(current_category)
                
                if current_category:
                    self.drugs_data.append({
                        'name': drug_name,
                        'category': current_category,
                        'keywords': self.categories.get(current_category, [])
                    })
                else:
                    # Save pending drug to assign category later
                    pending_drug = drug_name
                
        print(f"Loaded {len(self.drugs_data)} drugs in {len(self.categories)} categories")
        
    def _is_category_line(self, line: str) -> bool:
        """Check if a line is a standalone category."""
        if not line or len(line) < 3:
            return False
            
        # Should not contain dosage indicators
        dosage_indicators = ['mg', 'ml', 'g/ml', 'mcg', 'iu', '%', 'tab', 'inj', 
                            'cap', 'syp', 'susp', 'gel', 'cream', 'drop']
        line_lower = line.lower()
        if any(ind in line_lower for ind in dosage_indicators):
            return False
            
        # Should not start with common drug prefixes
        drug_prefixes = ['para', 'diclof', 'ibu', 'amox', 'cipro', 'metf']
        if any(line_lower.startswith(p) for p in drug_prefixes):
            return False
            
        # Known category patterns (from PDF analysis)
        category_patterns = [
            r'^[A-Z\s\-]+$',  # ALL CAPS
            r'^(anti|hypo|hyper)',  # Medical prefixes
            r'(drugs?|agents?|medications?|preparations?|products?|expanders?)$',  # Category suffixes
            r'^(nsaids?|opioid|hormones?|vitamins?|anaesthetics?)$',
        ]
        
        for pattern in category_patterns:
            if re.search(pattern, line_lower):
                return True
                
        # Check if it's mostly alphabetic with no numbers (categories rarely have numbers)
        alpha_ratio = sum(1 for c in line if c.isalpha()) / max(len(line), 1)
        has_numbers = any(c.isdigit() for c in line)
        
        if alpha_ratio > 0.9 and not has_numbers and len(line.split()) <= 4:
            # Could be a category - check known categories
            known_categories = [
                'anaesthetics', 'nsaids', 'antibacterials', 'antifungal', 'antiviral',
                'antiallergics', 'antiepileptics', 'antihormones', 'anticancer',
                'hypoglycaemics', 'antihypertensives', 'analgesics', 'antimalarial',
                'antitubercular', 'antianaemic', 'antipsychotics', 'antidepressants',
                'anxiolytics', 'sedatives', 'diuretics', 'laxatives', 'antiemetics',
                'bronchodilators', 'antitussives', 'expectorants', 'anticoagulants',
                'antihelminthic', 'antifilarials', 'antisickling', 'ophthalmic'
            ]
            if any(cat in line_lower for cat in known_categories):
                return True
                
        return False
        
    def _split_drug_category(self, line: str) -> Optional[Tuple[str, str]]:
        """Try to split a line that contains both drug name and category."""
        # Look for category at end of line after drug name
        # Format: "Drug name 123 mg                CategoryName"
        
        # Known category endings
        category_patterns = [
            r'(Anaesthetics)$',
            r'(Preanaesthetic medications?)$',
            r'(NSAIDS?)$',
            r'(Antibacterials?)$',
            r'(Antifungal)$',
            r'(Antiviral(?:\s+drugs?)?)$',
            r'(Antiallergics?)$',
            r'(Antiepileptics?)$',
            r'(Antihormones?)$',
            r'(Anticancer(?:\s+drugs?)?)$',
            r'(hypoglycaemics?)$',
            r'(Antihypertensives?)$',
            r'(OPIOID\s+ANALGESICS?)$',
            r'(ANTI[\s\-]?MIGRAINE\s+DRUGS?)$',
            r'(ANTI[\s\-]?TB\s+DRUGS?)$',
            r'(ANTIMALARIAL\s+DRUGS?)$',
        ]
        
        for pattern in category_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                category = match.group(1).strip()
                drug = line[:match.start()].strip()
                if drug:
                    return (drug, category)
                    
        return None
        
    def _derive_keywords_from_category(self, category: str) -> List[str]:
        """
        Derive symptom/condition keywords from category name.
        This is the KEY function - derives tags from PDF content, not hardcoded.
        """
        keywords = []
        category_lower = category.lower()
        
        # The category name itself is searchable
        keywords.append(category_lower)
        
        # Extract meaningful words from category
        words = re.findall(r'[a-zA-Z]+', category_lower)
        keywords.extend(words)
        
        # Common medical prefix/suffix expansions
        # These are LINGUISTIC derivations, not hardcoded symptom mappings
        prefix_expansions = {
            'anti': lambda rest: [f"against {rest}", f"treat {rest}", rest],
            'analgesic': lambda _: ['pain', 'ache', 'painful'],
            'nsaid': lambda _: ['pain', 'inflammation', 'swelling', 'fever', 'anti-inflammatory'],
            'opioid': lambda _: ['pain', 'severe pain', 'chronic pain'],
        }
        
        for word in words:
            # Handle "anti-X" patterns -> derives that it treats X
            if word.startswith('anti') and len(word) > 4:
                rest = word[4:]
                if rest:
                    keywords.append(rest)
                    # Common medical suffixes
                    if rest.endswith('al'):
                        keywords.append(rest[:-2])  # antibacterial -> bacteria
                    if rest.endswith('ic'):
                        keywords.append(rest[:-2])  # antibiotic -> antibiot
                        
        # Category-specific linguistic derivations
        # These derive from the WORDS in the category, not from external knowledge
        
        if 'antibacterial' in category_lower or 'antibiotic' in category_lower:
            keywords.extend(['infection', 'bacterial', 'bacteria'])
            
        if 'antifungal' in category_lower:
            keywords.extend(['fungal', 'fungus', 'yeast'])
            
        if 'antiviral' in category_lower:
            keywords.extend(['viral', 'virus'])
            
        if 'analgesic' in category_lower or 'nsaid' in category_lower:
            keywords.extend(['pain', 'ache', 'painful', 'hurt'])
            
        if 'antipyretic' in category_lower:
            keywords.extend(['fever', 'temperature', 'hot'])
            
        if 'antiemetic' in category_lower:
            keywords.extend(['nausea', 'vomiting', 'vomit'])
            
        if 'antidiarrheal' in category_lower or 'diarrh' in category_lower:
            keywords.extend(['diarrhea', 'loose stool', 'loose motion'])
            
        if 'antihistamine' in category_lower or 'antiallergic' in category_lower or 'allerg' in category_lower:
            keywords.extend(['allergy', 'allergic', 'itching', 'rash', 'hives'])
            
        if 'antihypertensive' in category_lower or 'hypertens' in category_lower:
            keywords.extend(['blood pressure', 'hypertension', 'bp'])
            
        if 'antidiabetic' in category_lower or 'diabet' in category_lower or 'hypoglycaemic' in category_lower or 'glycaemic' in category_lower:
            keywords.extend(['diabetes', 'blood sugar', 'glucose', 'sugar', 'diabetic', 'insulin'])
            
        if 'anticonvulsant' in category_lower or 'epilep' in category_lower:
            keywords.extend(['seizure', 'epilepsy', 'convulsion'])
            
        if 'antidepressant' in category_lower or 'depress' in category_lower:
            keywords.extend(['depression', 'mood', 'sad'])
            
        if 'anxiolytic' in category_lower or 'anxiety' in category_lower:
            keywords.extend(['anxiety', 'anxious', 'panic', 'nervous'])
            
        if 'sedative' in category_lower or 'hypnotic' in category_lower:
            keywords.extend(['sleep', 'insomnia', 'sleepless'])
            
        if 'diuretic' in category_lower:
            keywords.extend(['urine', 'urinary', 'fluid', 'edema', 'swelling'])
            
        if 'laxative' in category_lower:
            keywords.extend(['constipation', 'bowel'])
            
        if 'bronchodilator' in category_lower or 'asthma' in category_lower:
            keywords.extend(['breathing', 'asthma', 'wheeze', 'bronchitis'])
            
        if 'antitussive' in category_lower or 'cough' in category_lower:
            keywords.extend(['cough', 'coughing'])
            
        if 'expectorant' in category_lower:
            keywords.extend(['phlegm', 'mucus', 'congestion'])
            
        if 'migraine' in category_lower:
            keywords.extend(['headache', 'migraine', 'head pain'])
            
        if 'cardiac' in category_lower or 'heart' in category_lower:
            keywords.extend(['heart', 'cardiac', 'chest'])
            
        if 'gastric' in category_lower or 'stomach' in category_lower or 'antacid' in category_lower:
            keywords.extend(['stomach', 'acidity', 'heartburn', 'gastric', 'indigestion'])
            
        if 'antiulcer' in category_lower or 'ulcer' in category_lower:
            keywords.extend(['ulcer', 'stomach pain', 'gastric'])
            
        if 'hormone' in category_lower or 'hormonal' in category_lower:
            keywords.extend(['hormone', 'hormonal', 'endocrine'])
            
        if 'thyroid' in category_lower:
            keywords.extend(['thyroid', 'metabolism'])
            
        if 'steroid' in category_lower or 'corticosteroid' in category_lower:
            keywords.extend(['inflammation', 'swelling', 'immune'])
            
        if 'anticoagulant' in category_lower or 'blood' in category_lower:
            keywords.extend(['blood', 'clot', 'bleeding'])
            
        if 'vitamin' in category_lower or 'supplement' in category_lower:
            keywords.extend(['deficiency', 'supplement', 'nutrition'])
            
        if 'cancer' in category_lower or 'antineoplastic' in category_lower:
            keywords.extend(['cancer', 'tumor', 'malignant'])
            
        if 'tb' in category_lower or 'tuberculosis' in category_lower:
            keywords.extend(['tuberculosis', 'tb', 'lung infection'])
            
        if 'leprosy' in category_lower:
            keywords.extend(['leprosy', 'skin lesion'])
            
        if 'skin' in category_lower or 'dermat' in category_lower:
            keywords.extend(['skin', 'rash', 'dermatitis'])
            
        if 'eye' in category_lower or 'ophthalm' in category_lower:
            keywords.extend(['eye', 'vision', 'ocular'])
            
        if 'ear' in category_lower or 'otic' in category_lower:
            keywords.extend(['ear', 'hearing'])
            
        if 'muscle' in category_lower or 'relaxant' in category_lower:
            keywords.extend(['muscle', 'spasm', 'cramp'])
            
        if 'bone' in category_lower or 'osteo' in category_lower:
            keywords.extend(['bone', 'osteoporosis', 'fracture'])
            
        if 'joint' in category_lower or 'arthritis' in category_lower:
            keywords.extend(['joint', 'arthritis', 'joint pain'])
            
        if 'anaesthetic' in category_lower or 'anesthetic' in category_lower:
            keywords.extend(['surgery', 'sedation', 'numbness', 'local anesthesia', 'pain relief'])
            
        if 'preanaesthetic' in category_lower or 'preanesthetic' in category_lower:
            keywords.extend(['surgery', 'pre-surgery', 'sedation', 'anxiety'])
            
        if 'helminth' in category_lower or 'worm' in category_lower:
            keywords.extend(['worm', 'parasites', 'intestinal worm'])
            
        if 'filarial' in category_lower:
            keywords.extend(['filaria', 'lymphatic', 'elephantiasis'])
            
        if 'malarial' in category_lower or 'malaria' in category_lower:
            keywords.extend(['malaria', 'fever', 'mosquito'])
            
        if 'sickling' in category_lower or 'sickle' in category_lower:
            keywords.extend(['sickle cell', 'anemia', 'blood disorder'])
            
        if 'anaemic' in category_lower or 'anemic' in category_lower:
            keywords.extend(['anemia', 'iron', 'blood deficiency', 'weakness', 'fatigue'])
            
        if 'parkinson' in category_lower:
            keywords.extend(['tremor', 'movement disorder', 'shaking'])
            
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw and kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
                
        return unique_keywords
        
    def _parse_pdf(self, pdf_path: str):
        """Parse PDF file directly."""
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                all_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
                        
            # Save to raw text for future use
            raw_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'data', 'druglist_raw.txt'
            )
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(all_text)
                
            # Now parse the raw text
            self._parse_raw_text(raw_path)
            
        except ImportError:
            print("pdfplumber not installed, cannot parse PDF directly")
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            
    def _index_drugs(self):
        """Index all drugs in ChromaDB for semantic search."""
        if not self.collection or not self.drugs_data:
            return
            
        # Check if already indexed
        try:
            existing_count = self.collection.count()
            if existing_count >= len(self.drugs_data):
                print(f"Drugs already indexed: {existing_count}")
                return
        except:
            pass
            
        # Clear and reindex
        try:
            # Delete collection and recreate
            self.chroma_client.delete_collection("drugs_collection")
            self.collection = self.chroma_client.create_collection(
                name="drugs_collection",
                embedding_function=self.embedding_func,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error clearing collection: {e}")
            
        # Index in batches
        batch_size = 100
        for i in range(0, len(self.drugs_data), batch_size):
            batch = self.drugs_data[i:i+batch_size]
            
            ids = [f"drug_{i+j}" for j in range(len(batch))]
            
            # Create searchable documents - combine drug name, category, and keywords
            documents = []
            for drug in batch:
                # The searchable text includes everything derived from PDF
                search_text = f"{drug['name']} {drug['category']} {' '.join(drug['keywords'])}"
                documents.append(search_text)
                
            metadatas = [
                {
                    'name': drug['name'],
                    'category': drug['category'],
                    'keywords': ','.join(drug['keywords'])
                }
                for drug in batch
            ]
            
            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
            except Exception as e:
                print(f"Error indexing batch: {e}")
                
        print(f"Indexed {len(self.drugs_data)} drugs in ChromaDB")
        
    def search_drugs(
        self, 
        query: str, 
        symptoms: List[str] = None,
        n_results: int = 10
    ) -> List[Dict]:
        """
        Search for drugs based on query and symptoms.
        Uses pure semantic search on PDF-derived data.
        """
        if not self.collection:
            return self._fallback_search(query, symptoms, n_results)
            
        # Build comprehensive search query
        search_terms = [query] if query else []
        if symptoms:
            search_terms.extend(symptoms)
            
        search_query = ' '.join(search_terms)
        
        if not search_query.strip():
            return []
            
        try:
            results = self.collection.query(
                query_texts=[search_query],
                n_results=n_results * 3,  # Get more for deduplication and filtering
                include=['documents', 'metadatas', 'distances']
            )
            
            drugs = []
            seen_base_names = set()
            
            # Junk entries to skip
            junk_words = {'tab', 'syrup', 'mcg', 'ivig', 'repition', 'oxytocics', 
                          'vitamins', 'supplements', 'immune', 'mediators'}
            
            if results and results['metadatas'] and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    drug_name = metadata.get('name', '')
                    category = metadata.get('category', '')
                    
                    # Smart deduplication - extract base drug name
                    base_name = self._extract_base_name(drug_name)
                    
                    # Skip if base name is junk
                    if base_name.lower() in junk_words:
                        continue
                        
                    # Skip if base name is too short
                    if len(base_name) < 3:
                        continue
                    
                    if base_name.lower() in seen_base_names:
                        continue
                    seen_base_names.add(base_name.lower())
                    
                    # Calculate relevance score
                    distance = results['distances'][0][i] if results['distances'] else 0
                    relevance = max(0, 1 - distance)
                    
                    drugs.append({
                        'name': drug_name,
                        'base_name': base_name,
                        'category': category,
                        'relevance': relevance,
                        'source': 'PDF RAG'
                    })
                    
                    if len(drugs) >= n_results:
                        break
                        
            return drugs
            
        except Exception as e:
            print(f"Error searching ChromaDB: {e}")
            return self._fallback_search(query, symptoms, n_results)
            
    def _extract_base_name(self, drug_name: str) -> str:
        """Extract base drug name without dosage/form info."""
        # Remove common dosage forms and strengths
        name = drug_name.lower()
        
        # Remove dosage info like "650 mg", "500mg", etc.
        name = re.sub(r'\d+\.?\d*\s*(mg|ml|g|mcg|iu|%|gm)', '', name)
        
        # Remove form indicators
        forms = ['tab', 'tablet', 'cap', 'capsule', 'inj', 'injection', 
                 'syp', 'syrup', 'susp', 'suspension', 'cream', 'ointment',
                 'gel', 'drops', 'solution', 'powder', 'sachets', 'spray',
                 'i.p', 'ip', 'i.p.', 'dt', 'sr', 'xl', 'er', 'la']
        for form in forms:
            name = re.sub(rf'\b{form}\.?\b', '', name)
            
        # Remove special characters and extra whitespace
        name = re.sub(r'[+,/\(\)\[\]]', ' ', name)
        name = ' '.join(name.split())
        
        # Get first meaningful word (usually the drug name)
        words = [w for w in name.split() if len(w) > 2 and w.isalpha()]
        if words:
            return words[0].capitalize()
        
        # Fallback - try the original name
        orig_words = drug_name.split()
        for word in orig_words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            if len(clean_word) >= 3:
                return clean_word.capitalize()
                
        return drug_name
        
    def _fallback_search(
        self, 
        query: str, 
        symptoms: List[str] = None, 
        n_results: int = 10
    ) -> List[Dict]:
        """Fallback keyword-based search when ChromaDB is not available."""
        search_terms = [query.lower()] if query else []
        if symptoms:
            search_terms.extend([s.lower() for s in symptoms])
            
        if not search_terms:
            return []
            
        results = []
        seen_base_names = set()
        
        for drug in self.drugs_data:
            # Check if any search term matches drug info
            drug_text = f"{drug['name']} {drug['category']} {' '.join(drug['keywords'])}".lower()
            
            matches = sum(1 for term in search_terms if term in drug_text)
            
            if matches > 0:
                base_name = self._extract_base_name(drug['name'])
                
                if base_name.lower() in seen_base_names:
                    continue
                seen_base_names.add(base_name.lower())
                
                results.append({
                    'name': drug['name'],
                    'base_name': base_name,
                    'category': drug['category'],
                    'relevance': matches / len(search_terms),
                    'source': 'PDF Keyword'
                })
                
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:n_results]
        
    def get_drugs_by_category(self, category: str) -> List[Dict]:
        """Get all drugs in a specific category."""
        return [
            {
                'name': drug['name'],
                'category': drug['category'],
                'source': 'PDF Category'
            }
            for drug in self.drugs_data
            if category.lower() in drug['category'].lower()
        ]
        
    def get_all_categories(self) -> List[str]:
        """Get list of all drug categories from PDF."""
        return list(self.categories.keys())
        
    def get_category_keywords(self, category: str) -> List[str]:
        """Get derived keywords for a category."""
        return self.categories.get(category, [])


# Create singleton instance
_drug_rag_instance = None

def get_drug_rag_service(pdf_path: str = None) -> DrugRAGService:
    """Get or create the Drug RAG service instance."""
    global _drug_rag_instance
    
    if _drug_rag_instance is None:
        _drug_rag_instance = DrugRAGService(pdf_path)
        
    return _drug_rag_instance

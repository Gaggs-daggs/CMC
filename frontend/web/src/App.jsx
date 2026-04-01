import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './App.premium.css'
import atlasLogo from './assets/atlas-logo.png'
import './components/WelcomePage.css'
import './components/PrescriptionPage.css'
import WebGLBackground from './components/WebGLBackground'
import SessionSidebar from './components/SessionSidebar'
import BodySelector, { BodyIcon } from './components/BodySelector'
import SpecialistFinder from './components/SpecialistFinder'
import WelcomePage from './components/WelcomePage'
import PrescriptionPage from './components/PrescriptionPage'
import {
  MedicalCrossIcon,
  HeartPulseIcon,
  PillIcon,
  StethoscopeIcon,
  ActivityPulseIcon,
  ShieldCheckIcon,
  UserIcon as PremiumUserIcon,
  BotIcon as PremiumBotIcon,
  MicrophoneIcon,
  SendIcon as PremiumSendIcon,
  VolumeIcon as PremiumVolumeIcon,
  VolumeOffIcon as PremiumVolumeOffIcon,
  CameraIcon as PremiumCameraIcon,
  DownloadIcon as PremiumDownloadIcon,
  TrashIcon as PremiumTrashIcon,
  PhoneIcon as PremiumPhoneIcon,
  CloseIcon,
  AlertTriangleIcon,
  MessageSquareIcon,
  ClipboardMedicalIcon,
  LifebuoyIcon,
  HeartHandshakeIcon,
  StopCircleIcon as PremiumStopCircleIcon
} from './components/PremiumIcons'
import { InstallPrompt, OfflineIndicator, UpdateBanner } from './components/PWAComponents'

// API URL: Uses environment variable in production, localhost in development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const STORAGE_KEY = 'cmc_health_session'

// All Indian Languages with native script names
const langNames = { 
  en: 'English',
  hi: 'हिंदी (Hindi)',
  ta: 'தமிழ் (Tamil)',
  te: 'తెలుగు (Telugu)',
  bn: 'বাংলা (Bengali)',
  mr: 'मराठी (Marathi)',
  gu: 'ગુજરાતી (Gujarati)',
  kn: 'ಕನ್ನಡ (Kannada)',
  ml: 'മലയാളം (Malayalam)',
  pa: 'ਪੰਜਾਬੀ (Punjabi)',
  or: 'ଓଡ଼ିଆ (Odia)',
  as: 'অসমীয়া (Assamese)',
  ur: 'اردو (Urdu)',
  ne: 'नेपाली (Nepali)'
}

const getSpeechLang = (lang) => {
  const m = { 
    en:'en-IN', hi:'hi-IN', ta:'ta-IN', te:'te-IN', bn:'bn-IN', kn:'kn-IN', 
    ml:'ml-IN', gu:'gu-IN', mr:'mr-IN', pa:'pa-IN', ur:'ur-IN', or:'or-IN',
    as:'as-IN', ne:'ne-NP'
  }
  return m[lang] || 'en-IN'
}

// Symptom Information Database - Multilingual
const SYMPTOM_INFO = {
  headache: {
    en: { name: 'Headache', description: 'Pain in any part of the head, ranging from sharp to dull aching.', causes: 'Tension, dehydration, lack of sleep, eye strain, stress, or underlying conditions.', homeRemedies: 'Rest in a dark room, stay hydrated, apply cold compress, take OTC pain relievers.', whenToSeeDoctor: 'Severe sudden headache, headache with fever/stiff neck, or recurring headaches.' },
    hi: { name: 'सिरदर्द', description: 'सिर के किसी भी हिस्से में दर्द, तेज से लेकर हल्का दर्द।', causes: 'तनाव, निर्जलीकरण, नींद की कमी, आंखों पर जोर, तनाव।', homeRemedies: 'अंधेरे कमरे में आराम करें, पानी पिएं, ठंडी सिकाई करें।', whenToSeeDoctor: 'अचानक तेज सिरदर्द, बुखार के साथ सिरदर्द।' },
    ta: { name: 'தலைவலி', description: 'தலையின் எந்த பகுதியிலும் வலி.', causes: 'மன அழுத்தம், நீரிழப்பு, தூக்கமின்மை.', homeRemedies: 'இருண்ட அறையில் ஓய்வு, நீர் அருந்துங்கள்.', whenToSeeDoctor: 'திடீர் கடுமையான தலைவலி, காய்ச்சலுடன் தலைவலி.' },
    te: { name: 'తలనొప్పి', description: 'తల యొక్క ఏ భాగంలోనైనా నొప్పి.', causes: 'ఒత్తిడి, నిర్జలీకరణం, నిద్ర లేకపోవడం.', homeRemedies: 'చీకటి గదిలో విశ్రాంతి, నీరు తాగండి.', whenToSeeDoctor: 'అకస్మాత్తుగా తీవ్రమైన తలనొప్పి.' },
    bn: { name: 'মাথাব্যথা', description: 'মাথার যেকোনো অংশে ব্যথা।', causes: 'মানসিক চাপ, পানিশূন্যতা, ঘুমের অভাব।', homeRemedies: 'অন্ধকার ঘরে বিশ্রাম, পানি পান করুন।', whenToSeeDoctor: 'হঠাৎ তীব্র মাথাব্যথা, জ্বরের সাথে মাথাব্যথা।' }
  },
  fever: {
    en: { name: 'Fever', description: 'Body temperature above 100.4°F (38°C), indicating infection or illness.', causes: 'Viral/bacterial infections, inflammation, heat exhaustion, medications.', homeRemedies: 'Rest, drink fluids, cool compress, light clothing, paracetamol if needed.', whenToSeeDoctor: 'Temperature above 103°F, fever lasting 3+ days, with severe symptoms.' },
    hi: { name: 'बुखार', description: 'शरीर का तापमान 100.4°F से ऊपर, संक्रमण का संकेत।', causes: 'वायरल/बैक्टीरियल संक्रमण, सूजन।', homeRemedies: 'आराम करें, तरल पदार्थ पिएं, ठंडी सिकाई करें।', whenToSeeDoctor: '103°F से ऊपर बुखार, 3 दिनों से अधिक समय तक बुखार।' },
    ta: { name: 'காய்ச்சல்', description: 'உடல் வெப்பநிலை 100.4°F க்கு மேல்.', causes: 'வைரஸ்/பாக்டீரியா தொற்று.', homeRemedies: 'ஓய்வு, திரவங்கள் குடிக்கவும்.', whenToSeeDoctor: '103°F க்கு மேல் காய்ச்சல்.' },
    te: { name: 'జ్వరం', description: 'శరీర ఉష్ణోగ్రత 100.4°F పైన.', causes: 'వైరల్/బాక్టీరియల్ ఇన్ఫెక్షన్.', homeRemedies: 'విశ్రాంతి, ద్రవాలు తాగండి.', whenToSeeDoctor: '103°F పైన జ్వరం.' },
    bn: { name: 'জ্বর', description: 'শরীরের তাপমাত্রা 100.4°F এর উপরে।', causes: 'ভাইরাল/ব্যাকটেরিয়াল সংক্রমণ।', homeRemedies: 'বিশ্রাম, তরল পান করুন।', whenToSeeDoctor: '103°F এর উপরে জ্বর।' }
  },
  cough: {
    en: { name: 'Cough', description: 'Reflex action to clear airways of mucus, irritants, or foreign particles.', causes: 'Cold, flu, allergies, asthma, acid reflux, smoking, infections.', homeRemedies: 'Honey with warm water, ginger tea, steam inhalation, stay hydrated.', whenToSeeDoctor: 'Cough lasting 3+ weeks, blood in cough, difficulty breathing.' },
    hi: { name: 'खांसी', description: 'वायुमार्ग को साफ करने की प्रतिक्रिया।', causes: 'सर्दी, फ्लू, एलर्जी, अस्थमा।', homeRemedies: 'शहद गर्म पानी में, अदरक की चाय, भाप लें।', whenToSeeDoctor: '3 सप्ताह से अधिक खांसी, खांसी में खून।' },
    ta: { name: 'இருமல்', description: 'காற்றுப்பாதைகளை சுத்தம் செய்யும் எதிர்வினை.', causes: 'சளி, காய்ச்சல், ஒவ்வாமை.', homeRemedies: 'தேன் வெந்நீரில், இஞ்சி தேநீர்.', whenToSeeDoctor: '3 வாரங்களுக்கு மேல் இருமல்.' },
    te: { name: 'దగ్గు', description: 'వాయుమార్గాలను శుభ్రం చేసే రిఫ్లెక్స్.', causes: 'జలుబు, ఫ్లూ, అలెర్జీలు.', homeRemedies: 'వేడి నీటిలో తేనె, అల్లం టీ.', whenToSeeDoctor: '3 వారాలకు పైగా దగ్గు.' },
    bn: { name: 'কাশি', description: 'শ্বাসনালী পরিষ্কার করার প্রতিক্রিয়া।', causes: 'ঠান্ডা, ফ্লু, অ্যালার্জি।', homeRemedies: 'গরম পানিতে মধু, আদা চা।', whenToSeeDoctor: '3 সপ্তাহের বেশি কাশি।' }
  },
  'stomach pain': {
    en: { name: 'Stomach Pain', description: 'Pain or discomfort in the abdominal area between chest and pelvis.', causes: 'Indigestion, gas, food poisoning, gastritis, ulcers, infections.', homeRemedies: 'Warm water, ginger tea, avoid spicy foods, rest, light meals.', whenToSeeDoctor: 'Severe pain, blood in stool, fever with pain, pain lasting days.' },
    hi: { name: 'पेट दर्द', description: 'छाती और श्रोणि के बीच पेट क्षेत्र में दर्द।', causes: 'अपच, गैस, फूड पॉइज़निंग, गैस्ट्राइटिस।', homeRemedies: 'गर्म पानी, अदरक की चाय, मसालेदार भोजन से बचें।', whenToSeeDoctor: 'तेज दर्द, मल में खून, बुखार के साथ दर्द।' },
    ta: { name: 'வயிற்று வலி', description: 'வயிற்றுப் பகுதியில் வலி அல்லது அசௌகரியம்.', causes: 'அஜீரணம், வாயு, உணவு நச்சு.', homeRemedies: 'வெந்நீர், இஞ்சி தேநீர்.', whenToSeeDoctor: 'கடுமையான வலி, மலத்தில் இரத்தம்.' },
    te: { name: 'కడుపు నొప్పి', description: 'పొట్ట ప్రాంతంలో నొప్పి లేదా అసౌకర్యం.', causes: 'అజీర్ణం, గ్యాస్, ఆహార విషం.', homeRemedies: 'వేడి నీరు, అల్లం టీ.', whenToSeeDoctor: 'తీవ్రమైన నొప్పి, మలంలో రక్తం.' },
    bn: { name: 'পেট ব্যথা', description: 'পেটের অঞ্চলে ব্যথা বা অস্বস্তি।', causes: 'বদহজম, গ্যাস, ফুড পয়জনিং।', homeRemedies: 'গরম পানি, আদা চা।', whenToSeeDoctor: 'তীব্র ব্যথা, মলে রক্ত।' }
  },
  'joint pain': {
    en: { name: 'Joint Pain', description: 'Discomfort, aches, or soreness in any of the body\'s joints.', causes: 'Arthritis, injury, overuse, infection, autoimmune conditions.', homeRemedies: 'Rest the joint, ice/heat therapy, gentle stretching, OTC pain relievers.', whenToSeeDoctor: 'Severe swelling, inability to move joint, fever with joint pain.' },
    hi: { name: 'जोड़ों का दर्द', description: 'शरीर के किसी भी जोड़ में दर्द या पीड़ा।', causes: 'गठिया, चोट, अत्यधिक उपयोग।', homeRemedies: 'जोड़ को आराम दें, बर्फ/गर्मी चिकित्सा।', whenToSeeDoctor: 'गंभीर सूजन, जोड़ को हिलाने में असमर्थता।' },
    ta: { name: 'மூட்டு வலி', description: 'உடலின் மூட்டுகளில் வலி அல்லது வலி.', causes: 'மூட்டுவாதம், காயம், அதிக பயன்பாடு.', homeRemedies: 'மூட்டுக்கு ஓய்வு, ஐஸ்/வெப்ப சிகிச்சை.', whenToSeeDoctor: 'கடுமையான வீக்கம், மூட்டை நகர்த்த இயலாமை.' },
    te: { name: 'కీళ్ల నొప్పి', description: 'శరీరంలోని ఏదైనా కీళ్లలో నొప్పి.', causes: 'ఆర్థరైటిస్, గాయం, అధిక వినియోగం.', homeRemedies: 'కీలుకు విశ్రాంతి, ఐస్/హీట్ థెరపీ.', whenToSeeDoctor: 'తీవ్రమైన వాపు, కీలు కదపలేకపోవడం.' },
    bn: { name: 'জয়েন্টে ব্যথা', description: 'শরীরের যেকোনো জয়েন্টে ব্যথা।', causes: 'আর্থ্রাইটিস, আঘাত, অতিরিক্ত ব্যবহার।', homeRemedies: 'জয়েন্টকে বিশ্রাম দিন, বরফ/তাপ থেরাপি।', whenToSeeDoctor: 'গুরুতর ফোলা, জয়েন্ট নড়াতে অক্ষমতা।' }
  },
  'shoulder pain': {
    en: { name: 'Shoulder Pain', description: 'Pain in or around the shoulder joint, limiting arm movement.', causes: 'Rotator cuff injury, frozen shoulder, arthritis, tendinitis, overuse.', homeRemedies: 'Rest, ice pack, gentle stretching, OTC pain relievers, proper posture.', whenToSeeDoctor: 'Severe pain, inability to lift arm, swelling, pain after injury.' },
    hi: { name: 'कंधे का दर्द', description: 'कंधे के जोड़ में या उसके आसपास दर्द।', causes: 'रोटेटर कफ इंजरी, फ्रोजन शोल्डर, गठिया।', homeRemedies: 'आराम, आइस पैक, हल्की स्ट्रेचिंग।', whenToSeeDoctor: 'तेज दर्द, बांह उठाने में असमर्थता।' },
    ta: { name: 'தோள்பட்டை வலி', description: 'தோள்பட்டை மூட்டில் அல்லது அதைச் சுற்றி வலி.', causes: 'ரோட்டேட்டர் கஃப் காயம், உறைந்த தோள்பட்டை.', homeRemedies: 'ஓய்வு, ஐஸ் பேக், லேசான நீட்சி.', whenToSeeDoctor: 'கடுமையான வலி, கையை உயர்த்த இயலாமை.' },
    te: { name: 'భుజం నొప్పి', description: 'భుజం కీలు లో లేదా చుట్టూ నొప్పి.', causes: 'రోటేటర్ కఫ్ గాయం, ఫ్రోజెన్ షోల్డర్.', homeRemedies: 'విశ్రాంతి, ఐస్ ప్యాక్, తేలికపాటి స్ట్రెచింగ్.', whenToSeeDoctor: 'తీవ్రమైన నొప్పి, చేయి ఎత్తలేకపోవడం.' },
    bn: { name: 'কাঁধে ব্যথা', description: 'কাঁধের জয়েন্টে বা তার আশেপাশে ব্যথা।', causes: 'রোটেটর কাফ ইনজুরি, ফ্রোজেন শোল্ডার।', homeRemedies: 'বিশ্রাম, আইস প্যাক, হালকা স্ট্রেচিং।', whenToSeeDoctor: 'তীব্র ব্যথা, হাত তুলতে অক্ষমতা।' }
  },
  'allergic reaction': {
    en: { name: 'Allergic Reaction', description: 'Immune system response to a foreign substance (allergen).', causes: 'Food, pollen, dust, pet dander, medications, insect stings.', homeRemedies: 'Avoid allergen, antihistamines, cool compress for rashes.', whenToSeeDoctor: 'Difficulty breathing, swelling of face/throat, severe rash, anaphylaxis.' },
    hi: { name: 'एलर्जी प्रतिक्रिया', description: 'किसी विदेशी पदार्थ के प्रति प्रतिरक्षा प्रणाली की प्रतिक्रिया।', causes: 'भोजन, पराग, धूल, दवाएं, कीट के डंक।', homeRemedies: 'एलर्जेन से बचें, एंटीहिस्टामाइन लें।', whenToSeeDoctor: 'सांस लेने में कठिनाई, चेहरे/गले में सूजन।' },
    ta: { name: 'ஒவ்வாமை எதிர்வினை', description: 'அந்நிய பொருளுக்கு நோயெதிர்ப்பு அமைப்பு பதில்.', causes: 'உணவு, மகரந்தம், தூசி, மருந்துகள்.', homeRemedies: 'ஒவ்வாமையைத் தவிர்க்கவும், ஆன்டிஹிஸ்டமின்கள்.', whenToSeeDoctor: 'சுவாசிப்பதில் சிரமம், முகம்/தொண்டை வீக்கம்.' },
    te: { name: 'అలెర్జీ ప్రతిచర్య', description: 'విదేశీ పదార్థానికి రోగనిరోధక వ్యవస్థ ప్రతిస్పందన.', causes: 'ఆహారం, పుప్పొడి, దుమ్ము, మందులు.', homeRemedies: 'అలెర్జెన్‌ను నివారించండి, యాంటీహిస్టమిన్లు.', whenToSeeDoctor: 'శ్వాస తీసుకోవడంలో ఇబ్బంది, ముఖం/గొంతు వాపు.' },
    bn: { name: 'অ্যালার্জি প্রতিক্রিয়া', description: 'বিদেশী পদার্থের প্রতি রোগ প্রতিরোধ ব্যবস্থার প্রতিক্রিয়া।', causes: 'খাবার, পরাগ, ধুলো, ওষুধ।', homeRemedies: 'অ্যালার্জেন এড়িয়ে চলুন, অ্যান্টিহিস্টামিন।', whenToSeeDoctor: 'শ্বাসকষ্ট, মুখ/গলা ফোলা।' }
  },
  nausea: {
    en: { name: 'Nausea', description: 'Uneasiness in the stomach with an urge to vomit.', causes: 'Motion sickness, food poisoning, pregnancy, medications, infections.', homeRemedies: 'Ginger tea, small sips of water, crackers, fresh air, rest.', whenToSeeDoctor: 'Persistent vomiting, blood in vomit, severe dehydration, high fever.' },
    hi: { name: 'मतली', description: 'उल्टी करने की इच्छा के साथ पेट में बेचैनी।', causes: 'मोशन सिकनेस, फूड पॉइज़निंग, गर्भावस्था।', homeRemedies: 'अदरक की चाय, पानी की छोटी घूंट, क्रैकर्स।', whenToSeeDoctor: 'लगातार उल्टी, उल्टी में खून।' },
    ta: { name: 'குமட்டல்', description: 'வாந்தி எடுக்க வேண்டும் என்ற உணர்வுடன் வயிற்றில் அசௌகரியம்.', causes: 'மோஷன் சிக்னஸ், உணவு நச்சு, கர்ப்பம்.', homeRemedies: 'இஞ்சி தேநீர், சிறிய மடக்குகளில் தண்ணீர்.', whenToSeeDoctor: 'தொடர்ச்சியான வாந்தி, வாந்தியில் இரத்தம்.' },
    te: { name: 'వికారం', description: 'వాంతి చేయాలనే కోరికతో కడుపులో అసౌకర్యం.', causes: 'మోషన్ సిక్‌నెస్, ఆహార విషం, గర్భం.', homeRemedies: 'అల్లం టీ, నీటి చిన్న చుక్కలు.', whenToSeeDoctor: 'నిరంతర వాంతులు, వాంతిలో రక్తం.' },
    bn: { name: 'বমি বমি ভাব', description: 'বমি করার তাগিদ সহ পেটে অস্বস্তি।', causes: 'মোশন সিকনেস, ফুড পয়জনিং, গর্ভাবস্থা।', homeRemedies: 'আদা চা, অল্প পানি।', whenToSeeDoctor: 'ক্রমাগত বমি, বমিতে রক্ত।' }
  },
  anxiety: {
    en: { name: 'Anxiety', description: 'Feeling of worry, nervousness, or unease about something.', causes: 'Stress, trauma, genetics, medical conditions, caffeine, life changes.', homeRemedies: 'Deep breathing, meditation, exercise, limit caffeine, talk to someone.', whenToSeeDoctor: 'Persistent anxiety affecting daily life, panic attacks, depression.' },
    hi: { name: 'चिंता', description: 'किसी बात को लेकर चिंता, घबराहट या बेचैनी।', causes: 'तनाव, आघात, आनुवंशिकी, कैफीन।', homeRemedies: 'गहरी सांस लेना, ध्यान, व्यायाम।', whenToSeeDoctor: 'दैनिक जीवन को प्रभावित करने वाली लगातार चिंता।' },
    ta: { name: 'பதட்டம்', description: 'எதையாவது பற்றிய கவலை, பதட்டம் அல்லது அமைதியின்மை உணர்வு.', causes: 'மன அழுத்தம், அதிர்ச்சி, மரபியல்.', homeRemedies: 'ஆழ்ந்த சுவாசம், தியானம், உடற்பயிற்சி.', whenToSeeDoctor: 'அன்றாட வாழ்க்கையை பாதிக்கும் தொடர்ச்சியான பதட்டம்.' },
    te: { name: 'ఆందోళన', description: 'ఏదైనా గురించి ఆందోళన, భయం లేదా అశాంతి భావన.', causes: 'ఒత్తిడి, ట్రామా, జన్యుశాస్త్రం.', homeRemedies: 'లోతైన శ్వాస, ధ్యానం, వ్యాయామం.', whenToSeeDoctor: 'రోజువారీ జీవితాన్ని ప్రభావితం చేసే నిరంతర ఆందోళన.' },
    bn: { name: 'উদ্বেগ', description: 'কোনো কিছু নিয়ে চিন্তা, নার্ভাসনেস বা অস্বস্তির অনুভূতি।', causes: 'মানসিক চাপ, ট্রমা, জেনেটিক্স।', homeRemedies: 'গভীর শ্বাস, ধ্যান, ব্যায়াম।', whenToSeeDoctor: 'দৈনন্দিন জীবনকে প্রভাবিত করা ক্রমাগত উদ্বেগ।' }
  },
  vomiting: {
    en: { name: 'Vomiting', description: 'Forceful expulsion of stomach contents through the mouth.', causes: 'Food poisoning, infections, motion sickness, pregnancy, medications.', homeRemedies: 'Clear fluids, rest, avoid solid food initially, ginger, ORS.', whenToSeeDoctor: 'Blood in vomit, severe dehydration, fever, vomiting 24+ hours.' },
    hi: { name: 'उल्टी', description: 'मुंह से पेट की सामग्री का जबरन निष्कासन।', causes: 'फूड पॉइज़निंग, संक्रमण, मोशन सिकनेस।', homeRemedies: 'साफ तरल पदार्थ, आराम, अदरक, ORS।', whenToSeeDoctor: 'उल्टी में खून, गंभीर निर्जलीकरण।' },
    ta: { name: 'வாந்தி', description: 'வாய் வழியாக வயிற்றின் உள்ளடக்கங்களை வலுக்கட்டாயமாக வெளியேற்றுதல்.', causes: 'உணவு நச்சு, தொற்று, மோஷன் சிக்னஸ்.', homeRemedies: 'தெளிவான திரவங்கள், ஓய்வு, இஞ்சி, ORS.', whenToSeeDoctor: 'வாந்தியில் இரத்தம், கடுமையான நீரிழப்பு.' },
    te: { name: 'వాంతి', description: 'నోటి ద్వారా కడుపులోని పదార్థాలను బలవంతంగా బయటకు పంపడం.', causes: 'ఆహార విషం, ఇన్ఫెక్షన్, మోషన్ సిక్‌నెస్.', homeRemedies: 'క్లియర్ ఫ్లూయిడ్స్, విశ్రాంతి, అల్లం, ORS.', whenToSeeDoctor: 'వాంతిలో రక్తం, తీవ్రమైన నిర్జలీకరణం.' },
    bn: { name: 'বমি', description: 'মুখ দিয়ে পেটের বিষয়বস্তু জোরপূর্বক বের করা।', causes: 'ফুড পয়জনিং, সংক্রমণ, মোশন সিকনেস।', homeRemedies: 'পরিষ্কার তরল, বিশ্রাম, আদা, ORS।', whenToSeeDoctor: 'বমিতে রক্ত, গুরুতর ডিহাইড্রেশন।' }
  },
  dizziness: {
    en: { name: 'Dizziness', description: 'Feeling of being lightheaded, unsteady, or faint.', causes: 'Low blood pressure, dehydration, inner ear issues, anemia, medications.', homeRemedies: 'Sit or lie down, drink water, avoid sudden movements, eat something.', whenToSeeDoctor: 'Frequent episodes, fainting, chest pain, severe headache.' },
    hi: { name: 'चक्कर आना', description: 'सिर हल्का, अस्थिर या बेहोश होने का एहसास।', causes: 'निम्न रक्तचाप, निर्जलीकरण, कान की समस्या।', homeRemedies: 'बैठ जाएं या लेट जाएं, पानी पिएं।', whenToSeeDoctor: 'बार-बार एपिसोड, बेहोशी, छाती में दर्द।' },
    ta: { name: 'தலைச்சுற்றல்', description: 'தலை இலேசாக, நிலையற்றதாக அல்லது மயக்கமாக உணர்வது.', causes: 'குறைந்த இரத்த அழுத்தம், நீரிழப்பு.', homeRemedies: 'உட்காருங்கள் அல்லது படுங்கள், தண்ணீர் குடிக்கவும்.', whenToSeeDoctor: 'அடிக்கடி எபிசோடுகள், மயக்கம்.' },
    te: { name: 'తల తిరగడం', description: 'తల తేలికగా, అస్థిరంగా లేదా మూర్ఛపోతున్నట్లు అనిపించడం.', causes: 'తక్కువ బ్లడ్ ప్రెషర్, నిర్జలీకరణం.', homeRemedies: 'కూర్చోండి లేదా పడుకోండి, నీరు తాగండి.', whenToSeeDoctor: 'తరచుగా ఎపిసోడ్లు, మూర్ఛ.' },
    bn: { name: 'মাথা ঘোরা', description: 'মাথা হালকা, অস্থির বা অজ্ঞান হওয়ার অনুভূতি।', causes: 'নিম্ন রক্তচাপ, পানিশূন্যতা।', homeRemedies: 'বসুন বা শুয়ে পড়ুন, পানি পান করুন।', whenToSeeDoctor: 'ঘন ঘন পর্ব, অজ্ঞান হওয়া।' }
  },
  fatigue: {
    en: { name: 'Fatigue', description: 'Extreme tiredness resulting from physical or mental exertion.', causes: 'Lack of sleep, poor diet, stress, anemia, thyroid issues, depression.', homeRemedies: 'Get adequate sleep, balanced diet, exercise, reduce stress.', whenToSeeDoctor: 'Persistent fatigue for weeks, unexplained weight loss, severe weakness.' },
    hi: { name: 'थकान', description: 'शारीरिक या मानसिक परिश्रम से अत्यधिक थकावट।', causes: 'नींद की कमी, खराब आहार, तनाव।', homeRemedies: 'पर्याप्त नींद लें, संतुलित आहार।', whenToSeeDoctor: 'हफ्तों तक लगातार थकान।' },
    ta: { name: 'சோர்வு', description: 'உடல் அல்லது மன உழைப்பின் விளைவாக தீவிர சோர்வு.', causes: 'தூக்கமின்மை, மோசமான உணவு, மன அழுத்தம்.', homeRemedies: 'போதுமான தூக்கம், சமச்சீர் உணவு.', whenToSeeDoctor: 'வாரங்களாக தொடர்ச்சியான சோர்வு.' },
    te: { name: 'అలసట', description: 'శారీరక లేదా మానసిక శ్రమ వల్ల తీవ్రమైన అలసట.', causes: 'నిద్ర లేకపోవడం, పేద ఆహారం, ఒత్తిడి.', homeRemedies: 'తగినంత నిద్ర పొందండి, సమతుల్య ఆహారం.', whenToSeeDoctor: 'వారాల తరబడి నిరంతర అలసట.' },
    bn: { name: 'ক্লান্তি', description: 'শারীরিক বা মানসিক পরিশ্রমের ফলে চরম ক্লান্তি।', causes: 'ঘুমের অভাব, খারাপ খাদ্য, মানসিক চাপ।', homeRemedies: 'পর্যাপ্ত ঘুম, সুষম খাদ্য।', whenToSeeDoctor: 'সপ্তাহ ধরে ক্রমাগত ক্লান্তি।' }
  }
}

// Function to get symptom details in current language
const getSymptomInfo = (symptom, lang) => {
  const symptomLower = symptom.toLowerCase()
  
  // Try exact match first
  if (SYMPTOM_INFO[symptomLower]) {
    return SYMPTOM_INFO[symptomLower][lang] || SYMPTOM_INFO[symptomLower]['en']
  }
  
  // Try partial match
  for (const [key, value] of Object.entries(SYMPTOM_INFO)) {
    if (symptomLower.includes(key) || key.includes(symptomLower)) {
      return value[lang] || value['en']
    }
  }
  
  // Return generic info if not found
  return {
    name: symptom,
    description: lang === 'en' ? 'A symptom that requires medical attention.' : 'एक लक्षण जिसे चिकित्सा ध्यान देने की आवश्यकता है।',
    causes: lang === 'en' ? 'Various causes possible.' : 'विभिन्न कारण संभव।',
    homeRemedies: lang === 'en' ? 'Consult a healthcare provider for proper guidance.' : 'उचित मार्गदर्शन के लिए स्वास्थ्य सेवा प्रदाता से परामर्श करें।',
    whenToSeeDoctor: lang === 'en' ? 'If symptoms persist or worsen.' : 'यदि लक्षण बने रहें या बिगड़ जाएं।'
  }
}

// Premium icon wrappers with consistent sizing
const HeartIcon = () => <HeartPulseIcon size={24} />
const MicIcon = () => <MicrophoneIcon size={24} />
const SendIcon = () => <PremiumSendIcon size={24} />
const VolumeIcon = () => <PremiumVolumeIcon size={24} />
const VolumeOffIcon = () => <PremiumVolumeOffIcon size={24} />
const ActivityIcon = () => <ActivityPulseIcon size={24} />
const UserIcon = () => <PremiumUserIcon size={24} />
const BotIcon = () => <PremiumBotIcon size={24} />
const MessageIcon = () => <MessageSquareIcon size={24} />
const AlertIcon = () => <AlertTriangleIcon size={24} />
const DownloadIcon = () => <PremiumDownloadIcon size={24} />
const TrashIcon = () => <PremiumTrashIcon size={24} />
const PhoneIcon = () => <PremiumPhoneIcon size={24} />
const XIcon = () => <CloseIcon size={24} />
const CameraIcon = () => <PremiumCameraIcon size={24} />
const ImageIcon = () => <PremiumCameraIcon size={24} />
const PillIconComponent = () => <PillIcon size={24} />
const ShieldIcon = () => <ShieldCheckIcon size={24} />
const HeartHandIcon = () => <HeartHandshakeIcon size={24} />
const LifeBuoyIcon = () => <LifebuoyIcon size={24} />
const ClipboardIcon = () => <ClipboardMedicalIcon size={24} />
const StethoscopeIconComponent = () => <StethoscopeIcon size={24} />
const HeartPulseIconComponent = () => <HeartPulseIcon size={24} />
const StopIcon = () => <PremiumStopCircleIcon size={24} />
const StopCircleIcon = () => <PremiumStopCircleIcon size={24} />
const loadSession = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const data = JSON.parse(saved)
      if (data.messages) {
        data.messages = data.messages.map(m => ({ ...m, time: new Date(m.time) }))
      }
      return data
    }
  } catch (e) { console.error('Failed to load session:', e) }
  return null
}

// Save session to localStorage
const saveSession = (data) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch (e) { console.error('Failed to save session:', e) }
}

const detectLanguage = (text) => {
  if (!text) return 'en'
  if (/[\u0900-\u097F]/.test(text)) return 'hi'
  if (/[\u0B80-\u0BFF]/.test(text)) return 'ta'
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te'
  if (/[\u0980-\u09FF]/.test(text)) return 'bn'
  if (/[\u0C80-\u0CFF]/.test(text)) return 'kn'
  if (/[\u0D00-\u0D7F]/.test(text)) return 'ml'
  if (/[\u0A80-\u0AFF]/.test(text)) return 'gu'
  return 'en'
}

// Format AI response with sections
const FormattedMessage = ({ text, triage, medications, mentalHealth }) => {
  // Check if text has structured sections
  const hasStructure = text.includes('**') || text.includes('Understanding') || text.includes('Treatment') || text.includes('Doctor') || text.includes('Empathy');
  
  if (!hasStructure) {
    // Simple text - just render with basic formatting
    return <div className="simple-message">{text}</div>;
  }
  
  // Parse sections from the response
  const sections = [];
  
  // Try to extract sections using regex
  const conditionMatch = text.match(/\*\*Understanding[^*]*\*\*([^*]*?)(?=\*\*|$)/is) || 
                         text.match(/Understanding Your Condition[^:]*:?\s*([^*]*?)(?=\*\*Treatment|Treatment|$)/is);
  const treatmentMatch = text.match(/\*\*Treatment[^*]*\*\*([^*]*?)(?=\*\*|$)/is) ||
                         text.match(/Treatment & Medications[^:]*:?\s*([^*]*?)(?=\*\*Doctor|Doctor|$)/is);
  const doctorMatch = text.match(/\*\*Doctor[^*]*\*\*([^*]*?)(?=\*\*|$)/is) ||
                      text.match(/Doctor Recommendation[^:]*:?\s*([^*]*?)(?=\*\*Empathy|Empathy|$)/is);
  const empathyMatch = text.match(/\*\*Empathy[^*]*\*\*([^*]*?)$/is) ||
                       text.match(/Empathy & Support[^:]*:?\s*([^*]*?)$/is);
  
  // Clean up extracted text
  const cleanText = (t) => t?.trim()
    .replace(/\*\*/g, '')
    .replace(/^[]\s*/gm, '')
    .trim();
  
  const condition = cleanText(conditionMatch?.[1]);
  const treatment = cleanText(treatmentMatch?.[1]);
  const doctor = cleanText(doctorMatch?.[1]);
  const empathy = cleanText(empathyMatch?.[1]);
  
  // If we couldn't parse sections, show formatted raw text
  if (!condition && !treatment && !doctor && !empathy) {
    return (
      <div className="formatted-message">
        {text.split('\n').map((line, i) => {
          if (line.startsWith('**') && line.endsWith('**')) {
            return <h4 key={i} className="msg-section-title">{line.replace(/\*\*/g, '')}</h4>;
          }
          if (line.startsWith('•') || line.startsWith('-')) {
            return <li key={i} className="msg-list-item">{line.replace(/^[•-]\s*/, '')}</li>;
          }
          if (line.trim()) {
            return <p key={i} className="msg-para">{line}</p>;
          }
          return null;
        })}
      </div>
    );
  }
  
  return (
    <div className="structured-response">
      {condition && (
        <div className="response-section condition-section">
          <div className="section-header">
            <ClipboardIcon />
            <h4>Understanding Your Condition</h4>
          </div>
          <div className="section-content">
            {condition.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line.replace(/^[•-]\s*/, '• ')}</p>
            ))}
          </div>
        </div>
      )}
      
      {treatment && (
        <div className="response-section treatment-section">
          <div className="section-header">
            <PillIcon />
            <h4>Treatment & Medications</h4>
          </div>
          <div className="section-content">
            {treatment.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line.replace(/^[•-]\s*/, '• ')}</p>
            ))}
          </div>
        </div>
      )}
      
      {/* Show OTC medications if available */}
      {medications?.length > 0 && (
        <div className="medications-inline">
          {medications.map((med, j) => (
            <div key={j} className="med-card">
              <div className="med-card-name">{med.name}</div>
              <div className="med-card-dosage">{med.dosage}</div>
              {med.warnings?.[0] && <div className="med-card-warning">⚠️ {med.warnings[0]}</div>}
            </div>
          ))}
        </div>
      )}
      
      {doctor && (
        <div className="response-section doctor-section">
          <div className="section-header">
            <StethoscopeIcon />
            <h4>Doctor Recommendation</h4>
          </div>
          <div className="section-content">
            {doctor.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line.replace(/^[•-]\s*/, '• ')}</p>
            ))}
          </div>
        </div>
      )}
      
      {empathy && (
        <div className="response-section empathy-section">
          <div className="section-header">
            <HeartPulseIcon />
            <h4>Support & Care</h4>
          </div>
          <div className="section-content">
            {empathy.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </div>
      )}
      
      {/* Mental health resources */}
      {mentalHealth?.detected && mentalHealth.resources?.length > 0 && (
        <div className="response-section resources-section">
          <div className="section-header">
            <LifeBuoyIcon />
            <h4>Support Resources</h4>
          </div>
          <div className="helpline-cards">
            {mentalHealth.resources.slice(0, 2).map((res, i) => (
              <a key={i} href={`tel:${res.phone}`} className="helpline-card">
                <PhoneIcon />
                <div>
                  <div className="helpline-name">{res.name}</div>
                  <div className="helpline-number">{res.phone}</div>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default function App() {
  // Load saved session
  const savedSession = loadSession()
  
  // ─── Auth State ───────────────────────────────────────────
  // Auto-auth for iOS native app (detects WKWebView)
  const isIOSApp = typeof window !== 'undefined' && window.webkit && window.webkit.messageHandlers
  
  const [authUser, setAuthUser] = useState(() => {
    // iOS app: auto-authenticate
    if (isIOSApp) {
      return { name: 'Atlas User', email: 'atlas@ios.app', provider: 'ios_app', picture: null }
    }
    try {
      const stored = localStorage.getItem('cmc_auth')
      if (stored) {
        const parsed = JSON.parse(stored)
        return parsed.user || null
      }
    } catch {}
    return null
  })
  const [authToken, setAuthToken] = useState(() => {
    if (isIOSApp) return 'ios_app_token'
    try {
      const stored = localStorage.getItem('cmc_auth')
      if (stored) {
        const parsed = JSON.parse(stored)
        return parsed.access_token || null
      }
    } catch {}
    return null
  })

  // Auth callback from WelcomePage
  const handleAuthenticated = useCallback((user, token) => {
    setAuthUser(user)
    setAuthToken(token)
    // Use email as phone/userId for the existing chat system
    if (user?.email) {
      setPhone(user.email)
    }
  }, [])

  // Logout
  const handleLogout = useCallback(() => {
    localStorage.removeItem('cmc_auth')
    setAuthUser(null)
    setAuthToken(null)
    setView('home')
    setMessages([])
    setSessionId('')
    setPhone('')
  }, [])

  const [view, setView] = useState(isIOSApp ? 'chat' : (savedSession?.view || 'home'))
  const [phone, setPhone] = useState(isIOSApp ? 'atlas@ios.app' : (savedSession?.phone || ''))
  const [language, setLanguage] = useState(savedSession?.language || 'en')
  const [detectedLang, setDetectedLang] = useState(savedSession?.detectedLang || 'en')
  const [sessionId, setSessionId] = useState(savedSession?.sessionId || '')
  const [messages, setMessages] = useState(savedSession?.messages || [])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [vitals, setVitals] = useState(savedSession?.vitals || null)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [connected, setConnected] = useState(true)
  const [showDisclaimer, setShowDisclaimer] = useState(isIOSApp ? false : !localStorage.getItem('cmc_disclaimer_accepted'))
  const [detectedSymptoms, setDetectedSymptoms] = useState(savedSession?.symptoms || [])
  const [urgencyLevel, setUrgencyLevel] = useState(savedSession?.urgency || 'low')
  const [showEmergency, setShowEmergency] = useState(false)
  const [showImageUpload, setShowImageUpload] = useState(false)
  const [imageAnalyzing, setImageAnalyzing] = useState(false)
  const [imageResult, setImageResult] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [suggestedMeds, setSuggestedMeds] = useState(savedSession?.medications || [])
  const [medsExpanded, setMedsExpanded] = useState(false)
  const [triageInfo, setTriageInfo] = useState(savedSession?.triage || null)
  const [mentalHealthInfo, setMentalHealthInfo] = useState(savedSession?.mentalHealth || null)
  const [showMentalHealthSupport, setShowMentalHealthSupport] = useState(false)
  const [showCrisisBanner, setShowCrisisBanner] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
  // User preferences from profile (for TTS speed, voice, etc.)
  const [userPrefs, setUserPrefs] = useState(savedSession?.userPrefs || {
    tts_gender: 'female',
    tts_speed: 'normal',
    age_group: 'adult',
    has_allergies: false,
    has_conditions: false
  })
  
  // NEW: Follow-up questions and diagnoses
  const [followUpQuestions, setFollowUpQuestions] = useState([])
  const [diagnoses, setDiagnoses] = useState([])
  const [showDiagnosisPanel, setShowDiagnosisPanel] = useState(false)
  
  // NEW: Symptom details popup
  const [selectedSymptom, setSelectedSymptom] = useState(null)
  const [showSymptomDetails, setShowSymptomDetails] = useState(false)
  
  // NEW: Condition details modal
  const [selectedCondition, setSelectedCondition] = useState(null)
  const [showConditionDetails, setShowConditionDetails] = useState(false)
  const [conditionDetailsLoading, setConditionDetailsLoading] = useState(false)
  
  // NEW: 3D Body selector for pain location
  const [showBodySelector, setShowBodySelector] = useState(false)
  
  // NEW: Specialist finder for nearby doctors & online consultation
  const [showSpecialistFinder, setShowSpecialistFinder] = useState(false)
  
  // NEW: Prescription Analyzer page
  const [showPrescription, setShowPrescription] = useState(false)
  
  // NEW: Google Fit Vitals
  const [showVitals, setShowVitals] = useState(false)
  const [vitalsData, setVitalsData] = useState(null)
  const [vitalsLoading, setVitalsLoading] = useState(false)
  const [vitalsError, setVitalsError] = useState(null)

  const fetchVitals = async () => {
    const uid = phone.trim() || authUser?.email || 'gugan'
    setVitalsLoading(true)
    setVitalsError(null)
    try {
      const res = await fetch(`${API_BASE}/googlefit/vitals?user_id=${encodeURIComponent(uid)}`)
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        if (res.status === 401) {
          // Not connected — get auth URL and redirect
          const authRes = await fetch(`${API_BASE}/googlefit/auth-url?user_id=${encodeURIComponent(uid)}`)
          const authData = await authRes.json()
          if (authData.auth_url) {
            window.location.href = authData.auth_url
            return
          }
        }
        throw new Error(err.detail || 'Failed to fetch vitals')
      }
      const data = await res.json()
      setVitalsData(data)
      setShowVitals(true)
    } catch (e) {
      setVitalsError(e.message)
      setShowVitals(true)
    } finally {
      setVitalsLoading(false)
    }
  }

  // Drag-and-drop image upload
  const [isDragging, setIsDragging] = useState(false)
  const dragCounterRef = useRef(0)
  
  const chatEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const imageInputRef = useRef(null)
  const abortControllerRef = useRef(null)  // For cancelling API requests
  const audioRef = useRef(null)  // For TTS audio playback

  // Save session whenever state changes
  useEffect(() => {
    if (sessionId || messages.length > 0) {
      saveSession({ view, phone, language, detectedLang, sessionId, messages, vitals, symptoms: detectedSymptoms, urgency: urgencyLevel, triage: triageInfo, mentalHealth: mentalHealthInfo, userPrefs })
    }
  }, [view, phone, language, detectedLang, sessionId, messages, vitals, detectedSymptoms, urgencyLevel, triageInfo, mentalHealthInfo, userPrefs])

  // TEMP: Auto-open body selector on iOS for testing
  useEffect(() => {
    if (isIOSApp && view === 'chat') {
      setTimeout(() => setShowBodySelector(true), 2000)
    }
  }, [view])

  // Check for emergency symptoms
  useEffect(() => {
    if (urgencyLevel === 'emergency') {
      setShowEmergency(true)
    }
  }, [urgencyLevel])

  const initSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SR()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = getSpeechLang(detectedLang)
      recognitionRef.current.onresult = (e) => {
        const t = Array.from(e.results).map(r => r[0].transcript).join('')
        setInput(t)
        const d = detectLanguage(t)
        if (d !== detectedLang) setDetectedLang(d)
        if (e.results[0].isFinal) setIsListening(false)
      }
      recognitionRef.current.onerror = () => setIsListening(false)
      recognitionRef.current.onend = () => setIsListening(false)
      return true
    }
    return false
  }

  useEffect(() => {
    initSpeechRecognition()
  }, [detectedLang])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  // AbortController for TTS fetch — prevents overlapping requests
  const ttsAbortRef = useRef(null)
  const ttsRequestIdRef = useRef(0)  // Monotonic ID to discard stale responses

  const speak = async (text) => {
    if (!voiceEnabled || !text) return
    
    // Cancel any in-flight TTS fetch
    if (ttsAbortRef.current) {
      ttsAbortRef.current.abort()
      ttsAbortRef.current = null
    }
    
    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current = null
    }
    window.speechSynthesis && window.speechSynthesis.cancel()
    
    const lang = detectedLang || detectLanguage(text)
    const clean = text.replace(/\*\*/g,'').replace(/[\u{1F300}-\u{1F9FF}]/gu,'').replace(/\n+/g,'. ').trim()
    if (!clean) return
    
    // Truncate very long text for TTS (keep generous limit for non-Latin scripts like Tamil)
    const ttsText = clean.length > 800 ? clean.substring(0, 800) + '...' : clean
    
    setIsSpeaking(true)
    
    // Assign a unique ID so we can discard stale responses
    const requestId = ++ttsRequestIdRef.current
    const abortController = new AbortController()
    ttsAbortRef.current = abortController
    
    try {
      const ttsRequest = { 
        text: ttsText, 
        language: lang,
        gender: userPrefs.tts_gender || 'female',
        speed: userPrefs.tts_speed || 'normal'
      }
      
      console.log('🔊 TTS Request:', { 
        lang, 
        gender: ttsRequest.gender, 
        speed: ttsRequest.speed,
        textLen: ttsText.length
      })
      
      const res = await fetch(`${API_BASE}/tts/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ttsRequest),
        signal: abortController.signal
      })
      
      // Discard if a newer speak() was called while we were waiting
      if (requestId !== ttsRequestIdRef.current) {
        console.log('🔇 Discarding stale TTS response')
        setIsSpeaking(false)
        return
      }
      
      if (!res.ok) throw new Error('TTS failed')
      
      const audioBlob = await res.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      
      const audio = new Audio(audioUrl)
      audioRef.current = audio
      
      audio.onended = () => {
        setIsSpeaking(false)
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
      }
      audio.onerror = () => {
        setIsSpeaking(false)
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
      }
      
      await audio.play()
    } catch (e) {
      if (e.name === 'AbortError') {
        // speak() was intentionally cancelled — don't fallback
        console.log('🔇 TTS request cancelled')
        setIsSpeaking(false)
        return
      }
      console.error('Backend TTS error, using fallback:', e)
      // Fallback to browser SpeechSynthesis only if this is still the active request
      if (requestId === ttsRequestIdRef.current) {
        fallbackSpeak(ttsText, lang)
      } else {
        setIsSpeaking(false)
      }
    }
  }
  
  // Fallback to browser TTS if backend fails
  const fallbackSpeak = (clean, lang) => {
    if (!window.speechSynthesis) {
      console.warn('speechSynthesis not available (WebView)')
      setIsSpeaking(false)
      return
    }
    window.speechSynthesis.cancel()  // Ensure no overlap
    const doSpeak = () => {
      if (!window.SpeechSynthesisUtterance || !window.speechSynthesis) {
        setIsSpeaking(false)
        return
      }
      const u = new SpeechSynthesisUtterance(clean)
      u.lang = getSpeechLang(lang)
      u.rate = 0.95
      const voices = window.speechSynthesis.getVoices()
      const v = voices.find(x => x.lang.startsWith(lang)) || voices[0]
      if (v) u.voice = v
      u.onstart = () => setIsSpeaking(true)
      u.onend = () => setIsSpeaking(false)
      u.onerror = () => setIsSpeaking(false)
      window.speechSynthesis.speak(u)
    }
    if (window.speechSynthesis) {
      if (window.speechSynthesis.getVoices().length === 0) {
        window.speechSynthesis.onvoiceschanged = doSpeak
      } else doSpeak()
    } else {
      doSpeak()
    }
  }

  const stopSpeaking = () => {
    // Cancel any in-flight TTS fetch
    if (ttsAbortRef.current) {
      ttsAbortRef.current.abort()
      ttsAbortRef.current = null
    }
    ttsRequestIdRef.current++  // Invalidate any pending response
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current = null
    }
    window.speechSynthesis && window.speechSynthesis.cancel()
    setIsSpeaking(false)
  }

  const toggleListening = () => {
    // Lazily initialize speech recognizer (needed for Android WebView where
    // the native polyfill is injected after React's initial useEffect runs)
    if (!recognitionRef.current) {
      if (!initSpeechRecognition()) {
        alert('Speech not supported')
        return
      }
    }
    if (isListening) { recognitionRef.current.stop(); setIsListening(false) }
    else { recognitionRef.current.start(); setIsListening(true) }
  }

  // New state for profile management
  const [profileData, setProfileData] = useState(null)
  const [showProfileForm, setShowProfileForm] = useState(false)
  const [profileForm, setProfileForm] = useState({
    name: '',
    age: '',
    gender: 'not_specified',
    blood_type: '',
    height_cm: '',
    weight_kg: '',
    allergies: [],
    conditions: []
  })
  const [newAllergy, setNewAllergy] = useState('')
  const [newCondition, setNewCondition] = useState('')
  const [isReturningUser, setIsReturningUser] = useState(false)
  
  // BMI Calculation
  const calculateBMI = () => {
    const h = parseFloat(profileForm.height_cm)
    const w = parseFloat(profileForm.weight_kg)
    if (h > 0 && w > 0) {
      const heightM = h / 100
      return (w / (heightM * heightM)).toFixed(1)
    }
    return null
  }
  
  const getBMICategory = (bmi) => {
    if (!bmi) return null
    const b = parseFloat(bmi)
    if (b < 18.5) return { label: 'Underweight', color: '#3b82f6', icon: '📉' }
    if (b < 25) return { label: 'Normal', color: '#22c55e', icon: '✅' }
    if (b < 30) return { label: 'Overweight', color: '#f59e0b', icon: '⚠️' }
    return { label: 'Obese', color: '#ef4444', icon: '🔴' }
  }
  
  const bmi = calculateBMI()
  const bmiCategory = getBMICategory(bmi)
  
  // Autocomplete state
  const [allergySuggestions, setAllergySuggestions] = useState([])
  const [conditionSuggestions, setConditionSuggestions] = useState([])
  const [showAllergySuggestions, setShowAllergySuggestions] = useState(false)
  const [showConditionSuggestions, setShowConditionSuggestions] = useState(false)

  // Debounced autocomplete search
  const searchAllergens = async (query) => {
    if (query.length < 1) {
      setAllergySuggestions([])
      setShowAllergySuggestions(false)
      return
    }
    try {
      const res = await fetch(`${API_BASE}/autocomplete/allergens?q=${encodeURIComponent(query)}&limit=8`)
      const data = await res.json()
      if (data.success) {
        setAllergySuggestions(data.results)
        setShowAllergySuggestions(data.results.length > 0)
      }
    } catch (e) {
      console.error('Allergen search failed:', e)
    }
  }

  const searchConditions = async (query) => {
    if (query.length < 1) {
      setConditionSuggestions([])
      setShowConditionSuggestions(false)
      return
    }
    try {
      const res = await fetch(`${API_BASE}/autocomplete/conditions?q=${encodeURIComponent(query)}&limit=8`)
      const data = await res.json()
      if (data.success) {
        setConditionSuggestions(data.results)
        setShowConditionSuggestions(data.results.length > 0)
      }
    } catch (e) {
      console.error('Condition search failed:', e)
    }
  }

  // Debounce timers
  const allergyTimerRef = useRef(null)
  const conditionTimerRef = useRef(null)

  const handleAllergyInput = (value) => {
    setNewAllergy(value)
    if (allergyTimerRef.current) clearTimeout(allergyTimerRef.current)
    allergyTimerRef.current = setTimeout(() => searchAllergens(value), 200)
  }

  const handleConditionInput = (value) => {
    setNewCondition(value)
    if (conditionTimerRef.current) clearTimeout(conditionTimerRef.current)
    conditionTimerRef.current = setTimeout(() => searchConditions(value), 200)
  }

  const selectAllergySuggestion = (name) => {
    if (!profileForm.allergies.includes(name)) {
      setProfileForm(p => ({ ...p, allergies: [...p.allergies, name] }))
    }
    setNewAllergy('')
    setShowAllergySuggestions(false)
  }

  const selectConditionSuggestion = (name) => {
    if (!profileForm.conditions.includes(name)) {
      setProfileForm(p => ({ ...p, conditions: [...p.conditions, name] }))
    }
    setNewCondition('')
    setShowConditionSuggestions(false)
  }

  const checkProfileAndStart = async () => {
    // Use auth email as identifier if no phone set
    const userId = phone.trim() || authUser?.email || ''
    if (!userId) return alert('Please sign in first')
    if (!phone.trim() && authUser?.email) setPhone(authUser.email)
    setLoading(true)
    try {
      // First check if profile exists
      const checkRes = await fetch(`${API_BASE}/profile/check`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: userId })
      })
      const checkData = await checkRes.json()
      
      if (checkData.exists) {
        // Returning user - fetch FULL profile data
        setIsReturningUser(true)
        
        // Fetch full profile details
        try {
          const profileRes = await fetch(`${API_BASE}/profile/${encodeURIComponent(phone)}`)
          const profileJson = await profileRes.json()
          if (profileJson.success && profileJson.profile) {
            // Store full profile data for sidebar
            setProfileData({ ...checkData, profile: profileJson.profile })
            // Also populate the profile form for editing
            const p = profileJson.profile
            setProfileForm({
              name: p.name || '',
              age: p.age?.toString() || '',
              gender: p.gender || 'not_specified',
              blood_type: p.blood_type || '',
              height_cm: p.height_cm?.toString() || '',
              weight_kg: p.weight_kg?.toString() || '',
              allergies: p.allergies?.map(a => a.name || a) || [],
              conditions: p.medical_conditions?.map(c => c.name || c) || []
            })
          } else {
            setProfileData(checkData)
          }
        } catch (profileErr) {
          console.warn('Could not fetch full profile:', profileErr)
          setProfileData(checkData)
        }
        
        await startChat(checkData.profile_name)
      } else {
        // New user - show profile creation form
        setShowProfileForm(true)
        setLoading(false)
      }
    } catch (e) { 
      console.error('Profile check failed:', e)
      // Fallback to direct chat start if profile service fails
      await startChat()
    }
  }

  const createProfileAndStart = async () => {
    setLoading(true)
    try {
      // Create the profile
      const createRes = await fetch(`${API_BASE}/profile/create`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phone,
          name: profileForm.name || 'User',
          age: profileForm.age ? parseInt(profileForm.age) : null,
          gender: profileForm.gender,
          blood_type: profileForm.blood_type || null,
          height_cm: profileForm.height_cm ? parseFloat(profileForm.height_cm) : null,
          weight_kg: profileForm.weight_kg ? parseFloat(profileForm.weight_kg) : null,
          allergies: profileForm.allergies,
          chronic_conditions: profileForm.conditions
        })
      })
      
      if (!createRes.ok) {
        throw new Error('Failed to create profile')
      }
      
      setShowProfileForm(false)
      await startChat(profileForm.name)
    } catch (e) {
      console.error('Profile creation failed:', e)
      alert('Could not create profile. Starting without profile.')
      setShowProfileForm(false)
      await startChat()
    }
  }

  const addAllergy = () => {
    if (newAllergy.trim()) {
      setProfileForm(p => ({ ...p, allergies: [...p.allergies, newAllergy.trim()] }))
      setNewAllergy('')
    }
  }

  const addCondition = () => {
    if (newCondition.trim()) {
      setProfileForm(p => ({ ...p, conditions: [...p.conditions, newCondition.trim()] }))
      setNewCondition('')
    }
  }

  const removeAllergy = (idx) => setProfileForm(p => ({ ...p, allergies: p.allergies.filter((_, i) => i !== idx) }))
  const removeCondition = (idx) => setProfileForm(p => ({ ...p, conditions: p.conditions.filter((_, i) => i !== idx) }))

  const startChat = async (userName = null) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/conversation/start`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: phone, language, phone_number: phone })
      })
      const data = await res.json()
      setSessionId(data.session_id)
      
      // Personalized greeting for returning users
      let greeting = data.greeting
      if (userName && isReturningUser) {
        greeting = `Welcome back, ${userName}! ${data.greeting}`
      } else if (userName) {
        greeting = `Hello ${userName}! ${data.greeting}`
      }
      
      setMessages([{ role: 'assistant', text: greeting, time: new Date() }])
      setView('chat')
      setConnected(true)
      setTimeout(() => speak(greeting), 500)
    } catch (e) { setConnected(false); alert('Server offline') }
    setLoading(false)
  }

  // Handle body part selection from 3D body selector
  const handleBodyPartsSelected = (symptoms, bodyPartNames) => {
    console.log('🫀 Body parts selected:', bodyPartNames)
    console.log('🩺 Symptoms from body parts:', symptoms)
    
    // Add symptoms to detected symptoms
    setDetectedSymptoms(prev => {
      const newSymptoms = [...prev]
      symptoms.forEach(s => {
        if (!newSymptoms.includes(s)) {
          newSymptoms.push(s)
        }
      })
      return newSymptoms
    })
    
    // Build pain message in the user's selected language
    const bodyPartList = bodyPartNames.join(', ')
    const lang = detectedLang || language || 'en'
    
    // Pain message templates for supported languages
    const painTemplates = {
      'ta': `எனக்கு ${bodyPartList} பகுதியில் வலி உள்ளது`,
      'hi': `मुझे ${bodyPartList} में दर्द है`,
      'te': `నాకు ${bodyPartList} లో నొప్పి ఉంది`,
      'kn': `ನನಗೆ ${bodyPartList} ನಲ್ಲಿ ನೋವು ಇದೆ`,
      'ml': `എനിക്ക് ${bodyPartList} ൽ വേദന ഉണ്ട്`,
      'bn': `আমার ${bodyPartList} এ ব্যথা আছে`,
      'mr': `मला ${bodyPartList} मध्ये वेदना आहे`,
      'gu': `મને ${bodyPartList} માં દુખાવો છે`,
      'pa': `ਮੈਨੂੰ ${bodyPartList} ਵਿੱਚ ਦਰਦ ਹੈ`,
      'ur': `مجھے ${bodyPartList} میں درد ہے`,
    }
    
    const painMessage = painTemplates[lang] || `I have pain in my ${bodyPartList}`
    
    // Cancel any ongoing request first before sending new one
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    
    // Send this as a message to get diagnosis
    // Use a short delay to let the abort settle, then force-send even if loading
    setTimeout(() => {
      // Reset loading state so sendMsg doesn't get blocked
      setLoading(false)
      sendMsg(painMessage, true)
    }, 200)
  }

  // Fetch detailed info about a condition - uses fast llama3.2:3b model (~2-3 sec)
  const fetchConditionDetails = async (condition) => {
    setSelectedCondition(condition)
    setShowConditionDetails(true)
    setConditionDetailsLoading(true)
    
    try {
      // Use the fast condition-info endpoint
      const res = await fetch(`${API_BASE}/condition-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ condition: condition.condition })
      })
      
      const data = await res.json()
      
      setSelectedCondition({
        ...condition,
        detailedInfo: data.info || condition.description
      })
    } catch (error) {
      console.error('Error fetching condition details:', error)
      setSelectedCondition({
        ...condition,
        detailedInfo: condition.description || 'Details not available.'
      })
    } finally {
      setConditionDetailsLoading(false)
    }
  }

  const sendMsg = async (override, fromBodySelector = false) => {
    const msg = override || input
    if (!msg.trim() || loading) return
    
    // Check if user mentions pain - offer 3D body selector
    // Skip this if message came from body selector (to prevent reopening)
    if (!fromBodySelector) {
      const painKeywords = ['pain', 'hurt', 'hurts', 'ache', 'aching', 'sore', 'painful', 
                            'வலி', 'நோவு', 'दर्द', 'పెయిన్', 'നോവ്', 'ব্যথা']
      const msgLower = msg.toLowerCase()
      const mentionsPain = painKeywords.some(k => msgLower.includes(k))
      
      // If mentions pain but no specific body part, offer the selector
      const bodyParts = ['head', 'chest', 'back', 'stomach', 'arm', 'leg', 'knee', 'shoulder', 
                         'neck', 'eye', 'ear', 'throat', 'wrist', 'ankle', 'hip', 'elbow', 
                         'calf', 'thigh', 'shin', 'foot', 'toe', 'finger', 'hand', 'rib', 
                         'pelvis', 'groin', 'jaw', 'temple', 'forehead', 'abdomen', 'lower back',
                         'upper back', 'bicep', 'forearm', 'heel']
      const hasBodyPart = bodyParts.some(p => msgLower.includes(p))
      
      if (mentionsPain && !hasBodyPart) {
        // Show the 3D body selector to help locate pain
        setShowBodySelector(true)
        // Still continue with the message so user gets a response
      }
    }
    
    // Detect language from user's message
    const msgLang = detectLanguage(msg)
    
    // Determine output language priority:
    // 1. Use the dropdown-selected language (detectedLang) - this is what user explicitly wants
    // 2. If message is in a different non-English language, switch to that
    // 3. Fallback to 'en'
    let outputLang = detectedLang || language || 'en'
    
    // If user types in a different non-English language, update selection
    if (msgLang !== 'en' && msgLang !== detectedLang) {
      setDetectedLang(msgLang)
      outputLang = msgLang  // Use the detected language immediately (don't wait for state update)
    }
    
    console.log('📝 Message language:', msgLang, '| Output language:', outputLang, '| Dropdown selection:', detectedLang)
    
    setInput('')
    setMessages(m => [...m, { role: 'user', text: msg, time: new Date() }])
    setLoading(true)
    
    // Abort any previous in-flight request before starting new one
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    abortControllerRef.current = new AbortController()
    
    try {
      const res = await fetch(`${API_BASE}/conversation/message`, {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: msg, language: outputLang }),
        signal: abortControllerRef.current.signal
      })
      const data = await res.json()
      
      // Handle session not found - start new session
      if (data.detail === 'Session not found') {
        // Clear old session and prompt to restart
        localStorage.removeItem(STORAGE_KEY)
        setMessages(m => [...m, { role: 'assistant', text: 'Session expired. Please refresh and start a new chat.', time: new Date() }])
        setLoading(false)
        return
      }
      
      // Use translated response if available, otherwise fall back to original
      const txt = data.response_translated || data.response || 'No response'
      
      // Detailed logging for debugging translation issues - v2
      console.log('=== API Response Debug ===')
      console.log('🔤 Language sent to API:', outputLang)
      console.log('📥 Response (English):', data.response?.substring(0, 150))
      console.log('📥 Response (Translated):', data.response_translated ? data.response_translated.substring(0, 150) : '❌ NULL/EMPTY - Translation not working!')
      console.log('✅ Displaying text:', txt?.substring(0, 150))
      console.log('📊 Components used:', data.components_used)
      console.log('=========================')
      
      // IMPORTANT: Use translated response, fall back to English only if translation is null
      const displayText = (outputLang !== 'en' && data.response_translated) ? data.response_translated : txt
      
      setMessages(m => [...m, { 
        role: 'assistant', 
        text: displayText,  // Use displayText which prefers translated
        time: new Date(), 
        medications: data.medications || [],
        triage: data.triage || null,
        mentalHealth: data.mental_health || null
      }])
      
      // Update symptoms and urgency - replace with latest, don't accumulate stale ones
      if (data.symptoms_detected?.length > 0) {
        // Only keep meaningful symptoms (filter out context phrases)
        const cleanSymptoms = data.symptoms_detected
          .filter(s => s.split(' ').length <= 3) // Max 3 words
          .slice(0, 5) // Max 5 symptoms shown
        setDetectedSymptoms(cleanSymptoms)
      }
      if (data.urgency_level) {
        setUrgencyLevel(data.urgency_level)
        if (data.urgency_level === 'emergency') setShowEmergency(true)
      }
      
      // Update suggested medications - replace with current response
      if (data.medications?.length > 0) {
        console.log('💊 Setting medications:', data.medications)
        setSuggestedMeds(data.medications)
      } else {
        console.log('💊 No medications in response')
        setSuggestedMeds([]) // Clear if no medications in response
      }
      
      // NEW: Update follow-up questions
      if (data.follow_up_questions?.length > 0) {
        console.log('❓ Follow-up questions:', data.follow_up_questions)
        setFollowUpQuestions(data.follow_up_questions)
      } else {
        setFollowUpQuestions([])
      }
      
      // NEW: Update diagnoses with confidence
      if (data.diagnoses?.length > 0) {
        console.log('🏥 Diagnoses:', data.diagnoses)
        setDiagnoses(data.diagnoses)
        setShowDiagnosisPanel(true)
      }
      
      // Update triage information
      if (data.triage) {
        setTriageInfo(data.triage)
        if (data.triage.level === 'emergency') {
          setShowEmergency(true)
        }
      }
      
      // Update mental health information
      if (data.mental_health?.detected) {
        setMentalHealthInfo(data.mental_health)
        if (data.mental_health.is_crisis) {
          setShowCrisisBanner(true)
        } else if (data.mental_health.severity === 'moderate' || data.mental_health.severity === 'high') {
          setShowMentalHealthSupport(true)
        }
      }
      
      // Update user preferences from profile (for TTS speed, voice gender, etc.)
      if (data.user_preferences) {
        console.log('👤 User preferences from profile:', data.user_preferences)
        setUserPrefs(prev => ({
          ...prev,
          ...data.user_preferences
        }))
      }
      
      // Auto-speak the response (use displayText so correct language is spoken)
      speak(displayText)
    } catch (e) { 
      // Check if request was aborted
      if (e.name === 'AbortError') {
        // Only show "cancelled" if user explicitly cancelled (not replaced by a new request)
        // If a new request replaced this one, abortControllerRef will have a different controller
        // Don't add a cancelled message — the new request will provide the response
        console.log('🔇 Request aborted (replaced or cancelled)')
      } else {
        setMessages(m => [...m, { role: 'assistant', text: 'Error occurred', time: new Date() }]) 
      }
    }
    abortControllerRef.current = null
    setLoading(false)
  }

  // Cancel ongoing request (user explicitly clicks cancel)
  const cancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    stopSpeaking()
    setLoading(false)
    setMessages(m => [...m, { role: 'assistant', text: '⏹️ Response cancelled.', time: new Date() }])
  }

  // Export chat as text file
  const exportChat = () => {
    const content = [
      '=== Atlas Health Consultation ===',
      `Date: ${new Date().toLocaleString()}`,
      `Phone: ${phone}`,
      `Language: ${langNames[language]}`,
      detectedSymptoms.length > 0 ? `Symptoms: ${detectedSymptoms.join(', ')}` : '',
      '---',
      ...messages.map(m => `[${m.role === 'user' ? 'You' : 'AI'}] ${m.text}`),
      '---',
      'Disclaimer: This is AI-generated health information and not a substitute for professional medical advice.'
    ].filter(Boolean).join('\n\n')
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `health-consultation-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Clear session
  const clearSession = () => {
    if (confirm('Clear all conversation history?')) {
      localStorage.removeItem(STORAGE_KEY)
      setMessages([])
      setSessionId('')
      setDetectedSymptoms([])
      setUrgencyLevel('low')
      setVitals(null)
      setFollowUpQuestions([])
      setDiagnoses([])
      setShowDiagnosisPanel(false)
      setView('home')
    }
  }

  // Session sidebar handlers
  const handleNewSession = (session) => {
    if (session) {
      setSessionId(session.session_id)
      setMessages([{ role: 'assistant', text: 'How can I help you today?', time: new Date() }])
      setDetectedSymptoms([])
      setUrgencyLevel('low')
      setSuggestedMeds([])
      setTriageInfo(null)
      setMentalHealthInfo(null)
      setFollowUpQuestions([])
      setDiagnoses([])
      setShowDiagnosisPanel(false)
      setView('chat')
    } else {
      // Clear current session
      setMessages([])
      setSessionId('')
      setDetectedSymptoms([])
      setUrgencyLevel('low')
      setFollowUpQuestions([])
      setDiagnoses([])
      setShowDiagnosisPanel(false)
    }
  }

  const handleLoadSession = (session) => {
    if (session) {
      setSessionId(session.session_id)
      // Convert messages from API format to app format
      const loadedMessages = (session.messages || []).map(m => ({
        role: m.role,
        text: m.content,
        time: new Date(m.timestamp)
      }))
      setMessages(loadedMessages.length > 0 ? loadedMessages : [{ 
        role: 'assistant', 
        text: 'How can I help you today?', 
        time: new Date() 
      }])
      setDetectedSymptoms(session.symptoms || [])
      setUrgencyLevel(session.urgency_level || 'low')
      setView('chat')
    }
  }

  const handleProfileUpdate = (profile) => {
    setProfileData({ ...profileData, profile })
    if (profile.preferred_language) {
      setLanguage(profile.preferred_language)
      setDetectedLang(profile.preferred_language)
    }
  }

  // Image upload and analysis
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        alert('Image too large. Max 10MB')
        return
      }
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => setImagePreview(e.target.result)
      reader.readAsDataURL(file)
      setShowImageUpload(true)
    }
  }

  // Drag-and-drop image handlers
  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounterRef.current++
    const types = e.dataTransfer.types
    if (types.includes('Files') || types.includes('text/html') || types.includes('text/uri-list')) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounterRef.current--
    if (dragCounterRef.current === 0) {
      setIsDragging(false)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    dragCounterRef.current = 0

    // Case 1: File dragged from desktop/file manager
    const file = e.dataTransfer.files?.[0]
    if (file && file.type.startsWith('image/')) {
      if (file.size > 10 * 1024 * 1024) {
        alert('Image too large. Max 10MB')
        return
      }
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (ev) => setImagePreview(ev.target.result)
      reader.readAsDataURL(file)
      setShowImageUpload(true)
      return
    }

    // Case 2: Image dragged from another browser tab / web page
    const html = e.dataTransfer.getData('text/html')
    const url = e.dataTransfer.getData('text/uri-list') || e.dataTransfer.getData('text/plain')

    let imgUrl = null
    if (html) {
      const match = html.match(/<img[^>]+src=["']([^"']+)["']/)
      if (match) imgUrl = match[1]
    }
    if (!imgUrl && url && /\.(jpg|jpeg|png|gif|webp|bmp)/i.test(url)) {
      imgUrl = url
    }
    if (!imgUrl && url && url.startsWith('http')) {
      imgUrl = url
    }

    if (imgUrl) {
      try {
        const resp = await fetch(imgUrl)
        const blob = await resp.blob()
        if (!blob.type.startsWith('image/')) {
          alert('Could not load image. Try saving it to your computer first, then drag the file.')
          return
        }
        const imgFile = new File([blob], 'dropped-image.jpg', { type: blob.type })
        setSelectedImage(imgFile)
        setImagePreview(URL.createObjectURL(blob))
        setShowImageUpload(true)
      } catch {
        alert('Could not load image from that source. Try right-click → Save Image, then drag the saved file.')
      }
    }
  }

  const analyzeImage = async (context = '') => {
    if (!selectedImage) return
    setImageAnalyzing(true)
    setImageResult(null)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedImage)
      formData.append('context', context)
      formData.append('image_type', 'general')
      formData.append('session_id', sessionId || 'image_session')
      formData.append('language', language || 'en')
      
      const res = await fetch(`${API_BASE}/image/analyze`, {
        method: 'POST',
        body: formData
      })
      
      const data = await res.json()
      
      if (data.success) {
        setImageResult(data)
        
        // Use 'response' (from full pipeline) with fallback to 'analysis' (legacy)
        const responseText = data.response_translated || data.response || data.analysis || ''
        
        // Add to chat messages
        setMessages(m => [...m, 
          { role: 'user', text: context || '', time: new Date(), image: imagePreview },
          { role: 'assistant', text: responseText, time: new Date(), severity: data.severity || data.urgency_level }
        ])
        
        // ── Update all the same state as normal text chat ──
        
        // Update diagnoses with confidence scores
        if (data.diagnoses?.length > 0) {
          console.log('🏥 Image diagnoses:', data.diagnoses)
          setDiagnoses(data.diagnoses)
          setShowDiagnosisPanel(true)
        }
        
        // Update medications
        if (data.medications?.length > 0) {
          console.log('💊 Image medications:', data.medications)
          setSuggestedMeds(data.medications)
        }
        
        // Update follow-up questions
        if (data.follow_up_questions?.length > 0) {
          console.log('❓ Image follow-up questions:', data.follow_up_questions)
          setFollowUpQuestions(data.follow_up_questions)
        }
        
        // Update triage information
        if (data.triage) {
          setTriageInfo(data.triage)
          if (data.triage.level === 'emergency') {
            setShowEmergency(true)
          }
        }
        
        // Update detected symptoms
        if (data.symptoms_detected?.length > 0) {
          setDetectedSymptoms(prev => [...new Set([...(prev || []), ...data.symptoms_detected])])
        }
        
        speak(responseText)
      } else {
        alert(data.detail || 'Analysis failed')
      }
    } catch (e) {
      console.error('Image analysis error:', e)
      alert('Failed to analyze image. Please try again.')
    }
    
    setImageAnalyzing(false)
    setShowImageUpload(false)
    setSelectedImage(null)
    setImagePreview(null)
  }

  const closeImageModal = () => {
    setShowImageUpload(false)
    setSelectedImage(null)
    setImagePreview(null)
    setImageResult(null)
  }

  const getVitals = () => {
    setVitals({
      heartRate: Math.floor(60 + Math.random() * 40),
      spo2: Math.floor(94 + Math.random() * 6),
      temp: (97 + Math.random() * 3).toFixed(1),
      bp: `${Math.floor(110 + Math.random() * 30)}/${Math.floor(70 + Math.random() * 20)}`
    })
  }

  const formatTime = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  const quickActions = [{ label: 'Headache', msg: 'I have a headache' }, { label: 'Fever', msg: 'I have fever' }, { label: 'Stomach', msg: 'I have stomach pain' }, { label: 'Anxiety', msg: 'I feel anxious' }, { label: 'Sleep', msg: 'I cannot sleep' }]

  // Animation variants for Framer Motion
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.5, staggerChildren: 0.1 } }
  }
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  }
  
  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.4 } },
    hover: { scale: 1.02, boxShadow: "0 20px 40px rgba(0, 212, 170, 0.15)" }
  }
  
  const buttonVariants = {
    hover: { scale: 1.05, boxShadow: "0 10px 30px rgba(0, 212, 170, 0.4)" },
    tap: { scale: 0.95 }
  }

  if (view === 'home' && !authUser) {
    // ─── New Premium Welcome/Auth Page ──────────────────────
    return (
      <WelcomePage
        onAuthenticated={handleAuthenticated}
        language={language}
        setLanguage={(l) => { setLanguage(l); setDetectedLang(l) }}
        langNames={langNames}
      />
    )
  }

  if (view === 'home' && authUser) {
    // ─── Premium Authenticated Dashboard ──────────────────────
    return (
      <div className="wlc-page" style={{ minHeight: '100vh' }}>
        {/* Background effects — same as login page */}
        <div className="wlc-orbs">
          <div className="wlc-orb wlc-orb-1" />
          <div className="wlc-orb wlc-orb-2" />
          <div className="wlc-orb wlc-orb-3" />
        </div>
        <div className="wlc-particles">
          {Array.from({ length: 20 }, (_, i) => (
            <motion.div
              key={i}
              className="wlc-particle"
              style={{ left: `${Math.random()*100}%`, top: `${Math.random()*100}%`, width: Math.random()*3+1, height: Math.random()*3+1 }}
              animate={{ y: [0, -30, 0], opacity: [0, 0.5, 0] }}
              transition={{ duration: Math.random()*15+10, delay: Math.random()*5, repeat: Infinity, ease: 'easeInOut' }}
            />
          ))}
        </div>
        <svg className="wlc-grid-pattern" width="100%" height="100%">
          <defs><pattern id="grid2" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" /></pattern></defs>
          <rect width="100%" height="100%" fill="url(#grid2)" />
        </svg>

        {/* Nav Bar */}
        <motion.nav
          className="wlc-nav"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="wlc-nav-left">
            <motion.div className="wlc-nav-logo" animate={{ boxShadow: ['0 0 15px rgba(0,212,170,0.3)','0 0 30px rgba(0,212,170,0.5)','0 0 15px rgba(0,212,170,0.3)'] }} transition={{ duration: 2, repeat: Infinity }}>
              <img src={atlasLogo} alt="Atlas" className="wlc-nav-logo-img" />
            </motion.div>
            <span className="wlc-nav-brand">Atlas</span>
            <span className="wlc-nav-badge">AI-Powered</span>
          </div>
          <div className="wlc-nav-right" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.35rem 0.8rem 0.35rem 0.4rem', background: 'rgba(255,255,255,0.05)', borderRadius: '99px', border: '1px solid rgba(255,255,255,0.08)' }}>
              {authUser?.picture ? (
                <img src={authUser.picture} alt="" referrerPolicy="no-referrer" style={{ width: 28, height: 28, borderRadius: '50%', objectFit: 'cover' }} />
              ) : (
                <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg, #00d4aa, #6366f1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: 700, color: '#fff' }}>
                  {(authUser?.name || '?')[0].toUpperCase()}
                </div>
              )}
              <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)', fontWeight: 500 }}>{authUser?.name || 'User'}</span>
            </div>
            <button onClick={handleLogout} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '0.45rem 0.9rem', color: 'rgba(255,255,255,0.5)', fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s' }}
              onMouseEnter={e => { e.target.style.borderColor = 'rgba(239,68,68,0.3)'; e.target.style.color = '#fca5a5' }}
              onMouseLeave={e => { e.target.style.borderColor = 'rgba(255,255,255,0.08)'; e.target.style.color = 'rgba(255,255,255,0.5)' }}
            >Sign Out</button>
          </div>
        </motion.nav>

        {/* Main Dashboard Content */}
        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem', position: 'relative', zIndex: 5 }}>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            style={{ width: '100%', maxWidth: '900px' }}
          >
            {/* Profile Hero Card */}
            <motion.div
              style={{
                background: 'linear-gradient(165deg, rgba(20,25,40,0.95) 0%, rgba(12,16,28,0.98) 100%)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '24px',
                overflow: 'hidden',
                boxShadow: '0 24px 80px -12px rgba(0,0,0,0.5), 0 0 100px -20px rgba(0,212,170,0.08)',
                position: 'relative',
              }}
            >
              {/* Top glow */}
              <div style={{ position: 'absolute', top: -1, left: '50%', transform: 'translateX(-50%)', width: 250, height: 3, background: 'linear-gradient(90deg, transparent, #00d4aa, #6366f1, transparent)', borderRadius: '0 0 99px 99px', opacity: 0.8 }} />

              {/* Hero Banner */}
              <div style={{
                background: 'linear-gradient(135deg, rgba(0,212,170,0.08) 0%, rgba(99,102,241,0.06) 50%, rgba(139,92,246,0.04) 100%)',
                padding: '2.5rem 2.5rem 2rem',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                gap: '1.5rem',
              }}>
                {/* Profile Pic */}
                <motion.div
                  animate={{ scale: [1, 1.03, 1] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  style={{ position: 'relative', flexShrink: 0 }}
                >
                  {authUser?.picture ? (
                    <img src={authUser.picture} alt="" referrerPolicy="no-referrer" style={{ width: 80, height: 80, borderRadius: '50%', border: '3px solid rgba(0,212,170,0.4)', boxShadow: '0 8px 30px rgba(0,212,170,0.25)', objectFit: 'cover' }} />
                  ) : (
                    <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'linear-gradient(135deg, #00d4aa, #6366f1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', fontWeight: 700, color: '#fff', boxShadow: '0 8px 30px rgba(0,212,170,0.25)' }}>
                      {(authUser?.name || authUser?.email || '?')[0].toUpperCase()}
                    </div>
                  )}
                  <div style={{ position: 'absolute', bottom: 2, right: 2, width: 20, height: 20, borderRadius: '50%', background: '#22c55e', border: '3px solid rgba(12,16,28,0.98)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#fff' }} />
                  </div>
                </motion.div>

                {/* User Info */}
                <div style={{ flex: 1 }}>
                  <h1 style={{ fontFamily: "'Space Grotesk', 'Inter', sans-serif", fontSize: 'clamp(1.4rem, 3vw, 1.8rem)', fontWeight: 800, letterSpacing: '-0.02em', margin: 0, color: '#fff' }}>
                    Welcome back, <span style={{ background: 'linear-gradient(135deg, #00d4aa, #6366f1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>{authUser?.name || 'User'}</span>
                  </h1>
                  <p style={{ margin: '0.3rem 0 0', fontSize: '0.85rem', color: 'rgba(255,255,255,0.45)' }}>
                    {authUser?.email} • {authUser?.provider === 'google' ? '🔒 Google Account' : '🔒 Email Account'}
                  </p>
                </div>
              </div>

              {/* Quick Actions Grid */}
              <div style={{ padding: '2rem 2.5rem' }}>
                {/* Section Title */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem', color: '#00d4aa', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                  <span style={{ width: 20, height: 1, background: '#00d4aa' }} />
                  Configure Your Session
                </div>

                {/* Preferences Row */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                  {/* Language Selector */}
                  <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '14px', padding: '1rem 1.25rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.72rem', fontWeight: 600, color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.65rem' }}>
                      <span style={{ fontSize: '1rem' }}>🌐</span> Language
                    </label>
                    <select
                      value={language}
                      onChange={e => { setLanguage(e.target.value); setDetectedLang(e.target.value) }}
                      style={{ width: '100%', padding: '0.7rem 0.9rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px', color: '#fff', fontSize: '0.9rem', outline: 'none', cursor: 'pointer', boxSizing: 'border-box', appearance: 'none', backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.5)' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E\")", backgroundRepeat: 'no-repeat', backgroundPosition: 'right 0.8rem center' }}
                    >
                      {Object.entries(langNames).map(([c, n]) => <option key={c} value={c} style={{ background: '#1a1f2e' }}>{n}</option>)}
                    </select>
                  </div>

                  {/* Voice Toggle */}
                  <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '14px', padding: '1rem 1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.72rem', fontWeight: 600, color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.65rem' }}>
                      <span style={{ fontSize: '1rem' }}>🔊</span> Voice Responses
                    </label>
                    <div
                      onClick={() => setVoiceEnabled(!voiceEnabled)}
                      style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer', padding: '0.6rem 0.9rem', background: voiceEnabled ? 'rgba(0,212,170,0.1)' : 'rgba(255,255,255,0.05)', border: `1px solid ${voiceEnabled ? 'rgba(0,212,170,0.25)' : 'rgba(255,255,255,0.1)'}`, borderRadius: '10px', transition: 'all 0.2s' }}
                    >
                      <div style={{ width: 38, height: 20, borderRadius: 99, background: voiceEnabled ? '#00d4aa' : 'rgba(255,255,255,0.15)', position: 'relative', transition: 'all 0.2s', flexShrink: 0 }}>
                        <motion.div animate={{ x: voiceEnabled ? 18 : 0 }} transition={{ type: 'spring', stiffness: 500, damping: 30 }} style={{ width: 16, height: 16, borderRadius: '50%', background: '#fff', position: 'absolute', top: 2, left: 2, boxShadow: '0 1px 3px rgba(0,0,0,0.3)' }} />
                      </div>
                      <span style={{ fontSize: '0.85rem', color: voiceEnabled ? '#00d4aa' : 'rgba(255,255,255,0.5)', fontWeight: 500 }}>
                        {voiceEnabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Feature Quick-Access Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginBottom: '1.75rem' }}>
                  {[
                    { icon: '🧠', label: 'AI Diagnosis', color: '#00d4aa' },
                    { icon: '📸', label: 'Image Scan', color: '#6366f1' },
                    { icon: '🦴', label: 'Body Map', color: '#f59e0b' },
                    { icon: '💊', label: 'Drug Info', color: '#8b5cf6' },
                  ].map((feat, i) => (
                    <motion.div
                      key={i}
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.97 }}
                      style={{
                        background: `linear-gradient(135deg, ${feat.color}10, ${feat.color}05)`,
                        border: `1px solid ${feat.color}30`,
                        borderRadius: '12px',
                        padding: '1rem 0.75rem',
                        textAlign: 'center',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                      }}
                    >
                      <div style={{ fontSize: '1.5rem', marginBottom: '0.4rem' }}>{feat.icon}</div>
                      <div style={{ fontSize: '0.7rem', fontWeight: 600, color: 'rgba(255,255,255,0.7)', letterSpacing: '0.02em' }}>{feat.label}</div>
                    </motion.div>
                  ))}
                </div>

                {/* Start Button */}
                <motion.button
                  onClick={() => {
                    if (!phone && authUser?.email) setPhone(authUser.email)
                    checkProfileAndStart()
                  }}
                  disabled={loading}
                  whileHover={{ scale: loading ? 1 : 1.02 }}
                  whileTap={{ scale: loading ? 1 : 0.98 }}
                  style={{
                    width: '100%',
                    padding: '1rem 1.5rem',
                    background: 'linear-gradient(135deg, #00d4aa 0%, #00b894 100%)',
                    border: 'none',
                    borderRadius: '14px',
                    color: '#000',
                    fontSize: '1.05rem',
                    fontWeight: 700,
                    fontFamily: "'Inter', sans-serif",
                    cursor: loading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.6rem',
                    boxShadow: '0 8px 30px -4px rgba(0,212,170,0.4)',
                    transition: 'all 0.2s',
                    opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading ? (
                    <div style={{ width: 22, height: 22, border: '2.5px solid rgba(0,0,0,0.2)', borderTopColor: '#000', borderRadius: '50%', animation: 'wlc-spin 0.7s linear infinite' }} />
                  ) : (
                    <>
                      <StethoscopeIcon size={22} />
                      <span>Start Consultation</span>
                      <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
                    </>
                  )}
                </motion.button>
              </div>

              {/* Bottom Info Strip */}
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '2rem',
                padding: '1rem 2.5rem',
                borderTop: '1px solid rgba(255,255,255,0.04)',
                background: 'rgba(0,0,0,0.15)',
              }}>
                {[
                  { icon: '🔒', text: 'End-to-end encrypted' },
                  { icon: '⚡', text: 'AI responds in < 2s' },
                  { icon: '🏥', text: 'Clinical-grade analysis' },
                ].map((item, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.72rem', color: 'rgba(255,255,255,0.35)' }}>
                    <span>{item.icon}</span>
                    <span>{item.text}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Medical Disclaimer Modal */}
        <AnimatePresence>
          {showDisclaimer && (
            <motion.div
              style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                style={{ background: 'linear-gradient(165deg, rgba(20,25,40,0.98), rgba(12,16,28,0.98))', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '20px', padding: '2rem', maxWidth: 500, width: '100%', boxShadow: '0 25px 80px rgba(0,0,0,0.6)' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div style={{ width: 40, height: 40, borderRadius: '12px', background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>⚠️</div>
                  <h2 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>Medical Disclaimer</h2>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)', lineHeight: 1.7, marginBottom: '1.5rem' }}>
                  <p style={{ margin: '0 0 0.75rem' }}><strong style={{ color: '#fff' }}>Important:</strong> Atlas is an AI-powered health information tool and is NOT a substitute for professional medical advice, diagnosis, or treatment.</p>
                  <ul style={{ paddingLeft: '1.25rem', margin: 0, display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                    <li>Always consult a qualified healthcare provider</li>
                    <li>In emergency, call 108 (India) or local emergency number</li>
                    <li>Do not ignore professional advice based on AI suggestions</li>
                    <li>The AI may make mistakes — verify important information</li>
                  </ul>
                </div>
                <motion.button
                  onClick={() => { localStorage.setItem('cmc_disclaimer_accepted', 'true'); setShowDisclaimer(false) }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ width: '100%', padding: '0.85rem', background: 'linear-gradient(135deg, #00d4aa, #00b894)', border: 'none', borderRadius: '12px', color: '#000', fontSize: '0.95rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 20px rgba(0,212,170,0.3)' }}
                >
                  I Understand
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Profile Creation Modal */}
        <AnimatePresence>
          {showProfileForm && (
            <motion.div 
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0, 0, 0, 0.8)',
                backdropFilter: 'blur(8px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: '1rem'
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowProfileForm(false)}
            >
              <motion.div 
                onClick={(e) => e.stopPropagation()}
                initial={{ scale: 0.9, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.9, opacity: 0, y: 20 }}
                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                style={{
                  background: 'linear-gradient(145deg, rgba(26, 31, 46, 0.98) 0%, rgba(15, 20, 30, 0.98) 100%)',
                  borderRadius: '1.5rem',
                  border: '1px solid rgba(0, 212, 170, 0.2)',
                  boxShadow: '0 25px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(0, 212, 170, 0.1)',
                  maxWidth: '600px',
                  width: '100%',
                  maxHeight: '90vh',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                {/* Modal Header */}
                <div style={{
                  background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%)',
                  padding: '1.5rem 2rem',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem'
                }}>
                  <div style={{
                    width: '50px',
                    height: '50px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #00d4aa 0%, #6366f1 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 4px 20px rgba(0, 212, 170, 0.4)'
                  }}>
                    <PremiumUserIcon size={26} />
                  </div>
                  <div>
                    <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700', color: '#ffffff' }}>
                      Create Your Health Profile
                    </h2>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>
                      Personalized care starts with knowing you
                    </p>
                  </div>
                  <button 
                    onClick={() => setShowProfileForm(false)}
                    style={{
                      marginLeft: 'auto',
                      background: 'rgba(255, 255, 255, 0.1)',
                      border: 'none',
                      borderRadius: '50%',
                      width: '36px',
                      height: '36px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      color: 'rgba(255, 255, 255, 0.6)',
                      fontSize: '1.25rem',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={e => { e.target.style.background = 'rgba(255, 255, 255, 0.2)'; e.target.style.color = '#fff' }}
                    onMouseLeave={e => { e.target.style.background = 'rgba(255, 255, 255, 0.1)'; e.target.style.color = 'rgba(255, 255, 255, 0.6)' }}
                  >
                    ×
                  </button>
                </div>

                {/* Modal Body */}
                <div style={{ padding: '1.5rem 2rem', overflowY: 'auto', flex: 1 }}>
                  {/* Personal Info Section */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem', 
                      marginBottom: '1rem',
                      color: '#00d4aa',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>
                      <span style={{ width: '20px', height: '1px', background: '#00d4aa' }}></span>
                      Personal Information
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div style={{ gridColumn: 'span 2' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                          Full Name <span style={{ color: '#ef4444' }}>*</span>
                        </label>
                        <input 
                          type="text" 
                          value={profileForm.name} 
                          onChange={e => setProfileForm(p => ({ ...p, name: e.target.value }))}
                          placeholder="Enter your full name"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            transition: 'all 0.2s',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#00d4aa'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 212, 170, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>Age</label>
                        <input 
                          type="number" 
                          value={profileForm.age} 
                          onChange={e => setProfileForm(p => ({ ...p, age: e.target.value }))}
                          placeholder="Age"
                          min="0" max="150"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#00d4aa'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 212, 170, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>Gender</label>
                        <select 
                          value={profileForm.gender}
                          onChange={e => setProfileForm(p => ({ ...p, gender: e.target.value }))}
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            cursor: 'pointer',
                            boxSizing: 'border-box'
                          }}
                        >
                          <option value="not_specified" style={{ background: '#1a1f2e' }}>Prefer not to say</option>
                          <option value="male" style={{ background: '#1a1f2e' }}>Male</option>
                          <option value="female" style={{ background: '#1a1f2e' }}>Female</option>
                          <option value="other" style={{ background: '#1a1f2e' }}>Other</option>
                        </select>
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>Blood Type</label>
                        <select 
                          value={profileForm.blood_type}
                          onChange={e => setProfileForm(p => ({ ...p, blood_type: e.target.value }))}
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            cursor: 'pointer',
                            boxSizing: 'border-box'
                          }}
                        >
                          <option value="" style={{ background: '#1a1f2e' }}>Unknown</option>
                          <option value="A+" style={{ background: '#1a1f2e' }}>A+</option>
                          <option value="A-" style={{ background: '#1a1f2e' }}>A-</option>
                          <option value="B+" style={{ background: '#1a1f2e' }}>B+</option>
                          <option value="B-" style={{ background: '#1a1f2e' }}>B-</option>
                          <option value="AB+" style={{ background: '#1a1f2e' }}>AB+</option>
                          <option value="AB-" style={{ background: '#1a1f2e' }}>AB-</option>
                          <option value="O+" style={{ background: '#1a1f2e' }}>O+</option>
                          <option value="O-" style={{ background: '#1a1f2e' }}>O-</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Body Metrics Section with BMI */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem', 
                      marginBottom: '1rem',
                      color: '#6366f1',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>
                      <span style={{ width: '20px', height: '1px', background: '#6366f1' }}></span>
                      Body Metrics & BMI
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', alignItems: 'end' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                          Height (cm)
                        </label>
                        <input 
                          type="number" 
                          value={profileForm.height_cm} 
                          onChange={e => setProfileForm(p => ({ ...p, height_cm: e.target.value }))}
                          placeholder="170"
                          min="50" max="300"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#6366f1'; e.target.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                          Weight (kg)
                        </label>
                        <input 
                          type="number" 
                          value={profileForm.weight_kg} 
                          onChange={e => setProfileForm(p => ({ ...p, weight_kg: e.target.value }))}
                          placeholder="70"
                          min="20" max="500"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#6366f1'; e.target.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      {/* BMI Display Widget */}
                      <div style={{
                        background: bmi ? (
                          parseFloat(bmi) < 18.5 ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.05) 100%)' :
                          parseFloat(bmi) < 25 ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.05) 100%)' :
                          parseFloat(bmi) < 30 ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%)' :
                          'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.05) 100%)'
                        ) : 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
                        border: `1px solid ${bmi ? (
                          parseFloat(bmi) < 18.5 ? 'rgba(59, 130, 246, 0.3)' :
                          parseFloat(bmi) < 25 ? 'rgba(34, 197, 94, 0.3)' :
                          parseFloat(bmi) < 30 ? 'rgba(245, 158, 11, 0.3)' :
                          'rgba(239, 68, 68, 0.3)'
                        ) : 'rgba(255, 255, 255, 0.1)'}`,
                        borderRadius: '0.75rem',
                        padding: '0.75rem',
                        textAlign: 'center',
                        minHeight: '70px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center'
                      }}>
                        {bmi ? (
                          <>
                            <div style={{ 
                              fontSize: '1.5rem', 
                              fontWeight: '700',
                              color: parseFloat(bmi) < 18.5 ? '#3b82f6' :
                                     parseFloat(bmi) < 25 ? '#22c55e' :
                                     parseFloat(bmi) < 30 ? '#f59e0b' : '#ef4444'
                            }}>
                              {bmi}
                            </div>
                            <div style={{ 
                              fontSize: '0.7rem', 
                              color: 'rgba(255, 255, 255, 0.6)',
                              marginTop: '0.25rem',
                              fontWeight: '500'
                            }}>
                              BMI • {parseFloat(bmi) < 18.5 ? 'Underweight' :
                                     parseFloat(bmi) < 25 ? 'Normal' :
                                     parseFloat(bmi) < 30 ? 'Overweight' : 'Obese'}
                            </div>
                          </>
                        ) : (
                          <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.4)' }}>
                            Enter height & weight<br/>to calculate BMI
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Medical History Section */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem', 
                      marginBottom: '1rem',
                      color: '#ef4444',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>
                      <span style={{ width: '20px', height: '1px', background: '#ef4444' }}></span>
                      Medical History
                    </div>
                    
                    {/* Allergies Input */}
                    <div style={{ marginBottom: '1rem', position: 'relative', zIndex: 20 }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                        <AlertTriangleIcon size={14} />
                        Known Allergies
                      </label>
                      <div style={{ display: 'flex', gap: '0.5rem', position: 'relative' }}>
                        <div style={{ flex: 1, position: 'relative' }}>
                          <input 
                            type="text" 
                            value={newAllergy} 
                            onChange={e => handleAllergyInput(e.target.value)}
                            onFocus={e => { 
                              e.target.style.borderColor = '#ef4444'; 
                              e.target.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)'; 
                              newAllergy.length > 0 && searchAllergens(newAllergy) 
                            }}
                            onBlur={e => { 
                              e.target.style.borderColor = 'rgba(239, 68, 68, 0.2)'; 
                              e.target.style.boxShadow = 'none'; 
                              setTimeout(() => setShowAllergySuggestions(false), 200) 
                            }}
                            placeholder="Type to search allergies..."
                            onKeyPress={e => e.key === 'Enter' && addAllergy()}
                            style={{
                              width: '100%',
                              padding: '0.75rem 1rem',
                              background: 'rgba(239, 68, 68, 0.05)',
                              border: '1px solid rgba(239, 68, 68, 0.2)',
                              borderRadius: '0.75rem',
                              color: '#ffffff',
                              fontSize: '0.9rem',
                              outline: 'none',
                              boxSizing: 'border-box'
                            }}
                          />
                          {/* Allergy Autocomplete Dropdown */}
                          {showAllergySuggestions && allergySuggestions.length > 0 && (
                            <div style={{
                              position: 'absolute',
                              top: 'calc(100% + 4px)',
                              left: 0,
                              right: 0,
                              background: '#1a1f2e',
                              border: '1px solid rgba(239, 68, 68, 0.3)',
                              borderRadius: '0.75rem',
                              maxHeight: '180px',
                              overflowY: 'auto',
                              zIndex: 9999,
                              boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
                            }}>
                              {allergySuggestions.map((s, i) => (
                                <div 
                                  key={i}
                                  onMouseDown={() => selectAllergySuggestion(s.name)}
                                  style={{
                                    padding: '0.65rem 1rem',
                                    cursor: 'pointer',
                                    borderBottom: i < allergySuggestions.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                                    transition: 'background 0.15s',
                                    background: 'transparent'
                                  }}
                                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}
                                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                                >
                                  <div style={{ fontWeight: '500', color: '#ffffff', fontSize: '0.85rem' }}>{s.name}</div>
                                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>
                                    {s.category} • <span style={{ color: s.severity_typical === 'severe' ? '#ef4444' : s.severity_typical === 'moderate' ? '#f59e0b' : '#22c55e' }}>{s.severity_typical}</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <button 
                          onClick={addAllergy} 
                          style={{
                            padding: '0.75rem 1.25rem',
                            background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            borderRadius: '0.75rem',
                            color: '#ef4444',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={e => { e.target.style.background = 'rgba(239, 68, 68, 0.3)' }}
                          onMouseLeave={e => { e.target.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)' }}
                        >Add</button>
                      </div>
                      {profileForm.allergies.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                          {profileForm.allergies.map((a, i) => (
                            <motion.span 
                              key={i}
                              initial={{ scale: 0.8, opacity: 0 }}
                              animate={{ scale: 1, opacity: 1 }}
                              style={{ 
                                background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)',
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                color: '#fca5a5', 
                                padding: '0.35rem 0.75rem', 
                                borderRadius: '2rem', 
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontWeight: '500'
                              }}
                            >
                              {a}
                              <span onClick={() => removeAllergy(i)} style={{ cursor: 'pointer', fontWeight: 'bold', opacity: 0.7 }}>×</span>
                            </motion.span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Conditions Input */}
                    <div style={{ position: 'relative', zIndex: 10 }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                        <HeartPulseIcon size={14} />
                        Medical Conditions
                      </label>
                      <div style={{ display: 'flex', gap: '0.5rem', position: 'relative' }}>
                        <div style={{ flex: 1, position: 'relative' }}>
                          <input 
                            type="text" 
                            value={newCondition} 
                            onChange={e => handleConditionInput(e.target.value)}
                            onFocus={e => { 
                              e.target.style.borderColor = '#00d4aa'; 
                              e.target.style.boxShadow = '0 0 0 3px rgba(0, 212, 170, 0.1)'; 
                              newCondition.length > 0 && searchConditions(newCondition) 
                            }}
                            onBlur={e => { 
                              e.target.style.borderColor = 'rgba(0, 212, 170, 0.2)'; 
                              e.target.style.boxShadow = 'none'; 
                              setTimeout(() => setShowConditionSuggestions(false), 200) 
                            }}
                            placeholder="Type to search conditions..."
                            onKeyPress={e => e.key === 'Enter' && addCondition()}
                            style={{
                              width: '100%',
                              padding: '0.75rem 1rem',
                              background: 'rgba(0, 212, 170, 0.05)',
                              border: '1px solid rgba(0, 212, 170, 0.2)',
                              borderRadius: '0.75rem',
                              color: '#ffffff',
                              fontSize: '0.9rem',
                              outline: 'none',
                              boxSizing: 'border-box'
                            }}
                          />
                          {/* Condition Autocomplete Dropdown */}
                          {showConditionSuggestions && conditionSuggestions.length > 0 && (
                            <div style={{
                              position: 'absolute',
                              top: 'calc(100% + 4px)',
                              left: 0,
                              right: 0,
                              background: '#1a1f2e',
                              border: '1px solid rgba(0, 212, 170, 0.3)',
                              borderRadius: '0.75rem',
                              maxHeight: '180px',
                              overflowY: 'auto',
                              zIndex: 9999,
                              boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
                            }}>
                              {conditionSuggestions.map((s, i) => (
                                <div 
                                  key={i}
                                  onMouseDown={() => selectConditionSuggestion(s.name)}
                                  style={{
                                    padding: '0.65rem 1rem',
                                    cursor: 'pointer',
                                    borderBottom: i < conditionSuggestions.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                                    transition: 'background 0.15s',
                                    background: 'transparent'
                                  }}
                                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(0, 212, 170, 0.1)'}
                                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                                >
                                  <div style={{ fontWeight: '500', color: '#ffffff', fontSize: '0.85rem' }}>{s.name}</div>
                                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>
                                    {s.category} {s.icd10_code && <span style={{ color: '#00d4aa' }}>• {s.icd10_code}</span>}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <button 
                          onClick={addCondition} 
                          style={{
                            padding: '0.75rem 1.25rem',
                            background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 212, 170, 0.1) 100%)',
                            border: '1px solid rgba(0, 212, 170, 0.3)',
                            borderRadius: '0.75rem',
                            color: '#00d4aa',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={e => { e.target.style.background = 'rgba(0, 212, 170, 0.3)' }}
                          onMouseLeave={e => { e.target.style.background = 'linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 212, 170, 0.1) 100%)' }}
                        >Add</button>
                      </div>
                      {profileForm.conditions.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                          {profileForm.conditions.map((c, i) => (
                            <motion.span 
                              key={i}
                              initial={{ scale: 0.8, opacity: 0 }}
                              animate={{ scale: 1, opacity: 1 }}
                              style={{ 
                                background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 212, 170, 0.1) 100%)',
                                border: '1px solid rgba(0, 212, 170, 0.3)',
                                color: '#5eead4', 
                                padding: '0.35rem 0.75rem', 
                                borderRadius: '2rem', 
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontWeight: '500'
                              }}
                            >
                              {c}
                              <span onClick={() => removeCondition(i)} style={{ cursor: 'pointer', fontWeight: 'bold', opacity: 0.7 }}>×</span>
                            </motion.span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Modal Footer */}
                <div style={{ 
                  padding: '1.25rem 2rem', 
                  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                  background: 'rgba(0, 0, 0, 0.2)',
                  display: 'flex', 
                  gap: '1rem' 
                }}>
                  <motion.button 
                    onClick={() => { setShowProfileForm(false); startChat() }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                      flex: 1,
                      padding: '0.875rem 1.5rem',
                      background: 'transparent',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '0.75rem',
                      color: 'rgba(255, 255, 255, 0.7)',
                      fontWeight: '600',
                      cursor: 'pointer',
                      fontSize: '0.95rem',
                      transition: 'all 0.2s'
                    }}
                  >
                    Skip for Now
                  </motion.button>
                  <motion.button 
                    onClick={createProfileAndStart}
                    disabled={!profileForm.name.trim()}
                    whileHover={{ scale: profileForm.name.trim() ? 1.02 : 1 }}
                    whileTap={{ scale: profileForm.name.trim() ? 0.98 : 1 }}
                    style={{
                      flex: 2,
                      padding: '0.875rem 1.5rem',
                      background: profileForm.name.trim() 
                        ? 'linear-gradient(135deg, #00d4aa 0%, #00b894 100%)'
                        : 'rgba(255, 255, 255, 0.1)',
                      border: 'none',
                      borderRadius: '0.75rem',
                      color: profileForm.name.trim() ? '#000' : 'rgba(255, 255, 255, 0.3)',
                      fontWeight: '700',
                      cursor: profileForm.name.trim() ? 'pointer' : 'not-allowed',
                      fontSize: '0.95rem',
                      boxShadow: profileForm.name.trim() ? '0 4px 20px rgba(0, 212, 170, 0.4)' : 'none',
                      transition: 'all 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    {loading ? <div className="loading-spinner" style={{ width: '20px', height: '20px' }}></div> : (
                      <>
                        <span>Create Profile & Start</span>
                        <span style={{ fontSize: '1.1rem' }}>→</span>
                      </>
                    )}
                  </motion.button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer */}
        <div className="wlc-footer">
          <p>For informational purposes only. Always consult a qualified healthcare professional.</p>
          <p>© 2026 Atlas. All rights reserved.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app-container premium-theme with-sidebar">
      {/* PWA: Offline indicator, install prompt, update banner */}
      <OfflineIndicator />
      <InstallPrompt />
      <UpdateBanner />

      {/* Session Sidebar */}
      {view === 'chat' && phone && (
        <SessionSidebar
          phone={phone}
          currentSessionId={sessionId}
          onNewSession={handleNewSession}
          onLoadSession={handleLoadSession}
          onProfileUpdate={handleProfileUpdate}
          profileData={profileData}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
        />
      )}

      {/* Emergency Banner */}
      <AnimatePresence>
        {showEmergency && (
          <motion.div 
            className="emergency-banner"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
          >
            <div className="emergency-content">
              <AlertIcon />
              <span>Emergency symptoms detected! Please seek immediate medical attention.</span>
            </div>
            <div className="emergency-actions">
              <a href="tel:108" className="emergency-call"><PhoneIcon /> Call 108</a>
              <button className="emergency-hospital-btn" onClick={() => { setShowSpecialistFinder(true); setShowEmergency(false); }}>🏥 Find Hospital</button>
              <button onClick={() => setShowEmergency(false)}><XIcon /></button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Mental Health Crisis Banner */}
      {showCrisisBanner && (
        <div className="crisis-banner">
          <div className="crisis-content">
            <HeartHandIcon />
            <div className="crisis-text">
              <strong>You're not alone. Help is available.</strong>
              <span>If you're in crisis, please reach out to a helpline.</span>
            </div>
          </div>
          <div className="crisis-actions">
            <a href="tel:9152987821" className="crisis-call"><PhoneIcon /> iCall: 9152987821</a>
            <a href="tel:18602662345" className="crisis-call"><PhoneIcon /> Vandrevala: 1860-2662-345</a>
            <button onClick={() => setShowCrisisBanner(false)}><XIcon /></button>
          </div>
        </div>
      )}
      
      {/* Mental Health Support Panel */}
      {showMentalHealthSupport && mentalHealthInfo && !showCrisisBanner && (
        <div className="mental-health-panel">
          <div className="mh-panel-header">
            <HeartHandIcon />
            <span>Mental Health Support</span>
            <button onClick={() => setShowMentalHealthSupport(false)}><XIcon /></button>
          </div>
          <div className="mh-panel-content">
            {mentalHealthInfo.categories?.length > 0 && (
              <div className="mh-categories">
                {mentalHealthInfo.categories.map((cat, i) => (
                  <span key={i} className={`mh-tag ${cat}`}>{cat}</span>
                ))}
              </div>
            )}
            {mentalHealthInfo.grounding_exercise && (
              <div className="mh-exercise">
                <strong>🧘 Grounding Exercise:</strong>
                <p>{mentalHealthInfo.grounding_exercise}</p>
              </div>
            )}
            {mentalHealthInfo.breathing_exercise && (
              <div className="mh-exercise">
                <strong>🌬️ Breathing Exercise:</strong>
                <p>{mentalHealthInfo.breathing_exercise}</p>
              </div>
            )}
            {mentalHealthInfo.resources?.length > 0 && (
              <div className="mh-resources">
                <strong>📞 Support Resources:</strong>
                {mentalHealthInfo.resources.map((res, i) => (
                  <div key={i} className="mh-resource">
                    <span>{res.name}</span>
                    <a href={`tel:${res.phone}`}>{res.phone}</a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Image Upload Modal */}
      {showImageUpload && (
        <div className="modal-overlay" onClick={closeImageModal}>
          <div className="modal image-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <CameraIcon />
              <h2>Analyze Image</h2>
              <button className="close-btn" onClick={closeImageModal}><XIcon /></button>
            </div>
            <div className="modal-content">
              {imagePreview && (
                <div className="image-preview-container">
                  <img src={imagePreview} alt="Preview" className="image-preview" />
                </div>
              )}
              <p className="image-hint">AI will analyze this image for visible health conditions (skin, wounds, rashes, etc.)</p>
              <input
                type="text"
                className="image-context-input"
                placeholder="Add context: e.g., 'appeared 2 days ago, itchy'"
                onKeyDown={e => e.key === 'Enter' && analyzeImage(e.target.value)}
              />
              <div className="image-modal-actions">
                <button className="modal-btn secondary" onClick={closeImageModal}>Cancel</button>
                <button 
                  className="modal-btn primary" 
                  onClick={() => analyzeImage(document.querySelector('.image-context-input')?.value || '')}
                  disabled={imageAnalyzing}
                >
                  {imageAnalyzing ? 'Analyzing...' : 'Analyze Image'}
                </button>
              </div>
              <p className="disclaimer-text">⚠️ AI analysis is not a medical diagnosis. Consult a healthcare professional.</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Premium Background Decorations */}
      <div className="premium-chat-bg">
        <div className="chat-orb chat-orb-1" />
        <div className="chat-orb chat-orb-2" />
        <div className="chat-orb chat-orb-3" />
        <div className="chat-grid" />
      </div>

      {/* Premium Chat Navigation */}
      <motion.nav
        className="premium-chat-nav"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="nav-left">
          <motion.div
            className="nav-brand"
            onClick={() => { setView('home'); stopSpeaking() }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="nav-brand-icon"><img src={atlasLogo} alt="Atlas" className="nav-brand-logo" /></div>
            <span className="nav-brand-text">Atlas</span>
          </motion.div>
        </div>

        <div className="nav-center">
          <div className={`nav-status-pill ${connected ? '' : 'offline'}`}>
            <span className="status-dot-live" />
            <span>{connected ? 'AI Online' : 'Reconnecting...'}</span>
          </div>
        </div>

        <div className="nav-actions">
          <button className="nav-action-btn" onClick={exportChat} title="Export Chat"><DownloadIcon /></button>
          <button className="nav-action-btn" onClick={clearSession} title="Clear Session"><TrashIcon /></button>
          <select className="nav-lang-select" value={detectedLang} onChange={e => setDetectedLang(e.target.value)}>
            {Object.entries(langNames).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
          </select>
          {authUser && (
            <div className="nav-user-pill" title={authUser.name || authUser.email}>
              {authUser.picture ? (
                <img src={authUser.picture} alt="" className="nav-user-avatar" referrerPolicy="no-referrer" />
              ) : (
                <div className="nav-user-avatar-fallback">
                  {(authUser.name || authUser.email || '?')[0].toUpperCase()}
                </div>
              )}
              <span className="nav-user-name">{(authUser.name || '').split(' ')[0]}</span>
            </div>
          )}
        </div>
      </motion.nav>

      <motion.div
        className="premium-chat-layout"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.15 }}
      >
        <motion.div 
          className="premium-chat-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          style={{ position: 'relative' }}
        >
          {/* Drag-and-drop overlay */}
          {isDragging && (
            <div className="drag-overlay">
              <div className="drag-overlay-content">
                <CameraIcon />
                <p>Drop image here to analyze</p>
              </div>
            </div>
          )}
          
          {/* Symptoms & Triage Summary */}
          {(detectedSymptoms.length > 0 || triageInfo || urgencyLevel !== 'low') && (
            <motion.div 
              className={`symptoms-bar ${triageInfo?.level || urgencyLevel}`}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
            >
              {/* Urgency Level Badge */}
              <motion.div 
                className={`urgency-badge-dynamic ${urgencyLevel}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                key={urgencyLevel}
              >
                {urgencyLevel === 'emergency' && <span className="urgency-icon">🚨</span>}
                {urgencyLevel === 'urgent' && <span className="urgency-icon">⚠️</span>}
                {urgencyLevel === 'doctor_soon' && <span className="urgency-icon">🩺</span>}
                {urgencyLevel === 'routine' && <span className="urgency-icon">📋</span>}
                {urgencyLevel === 'self_care' && <span className="urgency-icon">✅</span>}
                <span className="urgency-text">
                  {urgencyLevel === 'emergency' ? 'Emergency' : 
                   urgencyLevel === 'urgent' ? 'Urgent' : 
                   urgencyLevel === 'doctor_soon' ? 'See Doctor Soon' :
                   urgencyLevel === 'routine' ? 'Routine' : 'Self Care'}
                </span>
              </motion.div>

              {/* Detected Symptoms */}
              {detectedSymptoms.length > 0 && (
                <div className="detected-symptoms-section">
                  <span className="symptoms-label">DETECTED:</span>
                  <div className="symptom-tags-container">
                    {detectedSymptoms.slice(0, 5).map((s, i) => (
                      <motion.span 
                        key={i} 
                        className="symptom-tag clickable"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        onClick={() => {
                          setSelectedSymptom(s)
                          setShowSymptomDetails(true)
                        }}
                        title="Click for more info"
                      >
                        {s}
                      </motion.span>
                    ))}
                    {detectedSymptoms.length > 5 && (
                      <span 
                        className="symptom-tag more clickable"
                        onClick={() => setShowDiagnosisPanel(true)}
                        title="View all symptoms"
                      >
                        +{detectedSymptoms.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {urgencyLevel === 'emergency' && (
                <motion.span 
                  className="urgency-badge emergency"
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                >
                  🚨 Emergency
                </motion.span>
              )}
            </motion.div>
          )}

          {/* Google Fit Vitals Panel */}
          {showVitals && (
            <motion.div
              className="vitals-panel"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="vitals-header">
                <div className="vitals-header-left">
                  <HeartPulseIcon size={16} />
                  <span>Watch Vitals</span>
                </div>
                <button className="vitals-close-btn" onClick={() => setShowVitals(false)} title="Close">
                  <XIcon />
                </button>
              </div>
              {vitalsLoading ? (
                <div className="vitals-loading">
                  <span className="vitals-spinner"></span> Fetching from watch...
                </div>
              ) : vitalsError ? (
                <div className="vitals-error">
                  ⚠️ {vitalsError}
                  <button className="vitals-retry" onClick={fetchVitals}>Retry</button>
                </div>
              ) : vitalsData ? (
                <div className="vitals-grid">
                  {vitalsData.heart_rate?.latest && (
                    <div className="vital-card heart">
                      <span className="vital-icon">❤️</span>
                      <span className="vital-value">{Math.round(vitalsData.heart_rate.latest)}</span>
                      <span className="vital-unit">bpm</span>
                      <span className="vital-label">Heart Rate</span>
                    </div>
                  )}
                  {vitalsData.spo2?.latest && (
                    <div className="vital-card spo2">
                      <span className="vital-icon">🫁</span>
                      <span className="vital-value">{Math.round(vitalsData.spo2.latest)}</span>
                      <span className="vital-unit">%</span>
                      <span className="vital-label">SpO₂</span>
                    </div>
                  )}
                  {vitalsData.heart_rate?.resting && (
                    <div className="vital-card resting">
                      <span className="vital-icon">💓</span>
                      <span className="vital-value">{Math.round(vitalsData.heart_rate.resting)}</span>
                      <span className="vital-unit">bpm</span>
                      <span className="vital-label">Resting HR</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="vitals-empty">No vitals data available</div>
              )}
              {vitalsData?.alerts && vitalsData.alerts.length > 0 && (
                <div className="vitals-alerts">
                  {vitalsData.alerts.map((a, i) => (
                    <div key={i} className={`vital-alert ${a.severity || 'info'}`}>
                      ⚠️ {a.message}
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* Medications Panel - Compact & Collapsible */}
          {suggestedMeds.length > 0 && (
            <motion.div 
              className={`medications-panel compact ${medsExpanded ? 'expanded' : ''}`}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="medications-header">
                <div className="meds-header-left" onClick={() => setMedsExpanded(!medsExpanded)}>
                  <PillIconComponent />
                  <span>Medications ({suggestedMeds.length})</span>
                  <span className="expand-icon">{medsExpanded ? '▲' : '▼'}</span>
                </div>
                <button 
                  className="meds-close-btn"
                  onClick={() => setSuggestedMeds([])}
                  title="Close medications panel"
                >
                  <XIcon />
                </button>
              </div>
              {medsExpanded && (
                <div className="medications-list">
                  {suggestedMeds.slice(0, 6).map((med, i) => (
                    <motion.div 
                      key={i} 
                      className="medication-card mini"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.05 }}
                      title={`${med.name || med}${med.warning ? ` - ⚠️ ${med.warning}` : ''}`}
                    >
                      <div className="med-name">{med.name || med}</div>
                      {med.dosage && <div className="med-dosage">{med.dosage}</div>}
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          )}
          
          {/* Diagnosis Panel - Compact */}
          {showDiagnosisPanel && diagnoses.length > 0 && (
            <motion.div 
              className="diagnosis-panel compact"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="diagnosis-header">
                <div className="diagnosis-header-left">
                  <ClipboardIcon />
                  <span>Possible Conditions</span>
                </div>
                <button 
                  className="diagnosis-close-btn"
                  onClick={() => setShowDiagnosisPanel(false)}
                  title="Close"
                >
                  <XIcon />
                </button>
              </div>
              <div className="diagnosis-list compact-list">
                {diagnoses.slice(0, 5).map((d, i) => (
                  <motion.div 
                    key={i} 
                    className={`diagnosis-card mini ${d.urgency || 'self_care'} clickable`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => fetchConditionDetails(d)}
                    title="Click for details"
                    style={{ cursor: 'pointer' }}
                  >
                    <span className="diagnosis-rank-mini">#{i + 1}</span>
                    <span className="diagnosis-name-mini">{d.condition}</span>
                    <span className="diagnosis-pct-mini">{Math.round(d.confidence * 100)}%</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
          
          <div className="chat-wrapper">
            <div className="chat-webgl-bg">
              <WebGLBackground contained />
            </div>
            <div className="premium-chat-container chat-container">
              {messages.length === 0 ? (
                <div className="premium-welcome-msg">
                  <div className="welcome-robot-animation">
                    <dotlottie-wc 
                      src="https://lottie.host/534fef36-80e8-4072-a726-2afecbe9467b/8J3QDVdUdW.lottie" 
                      style={{ width: '200px', height: '200px' }}
                      autoplay 
                      loop
                    />
                  </div>
                  <h2>How can I help you today?</h2>
                  <p>Describe your symptoms, upload an image, or ask any health question.</p>
                </div>
              ) : (
                messages.map((m, i) => (
                  <div key={i} className={`premium-msg message ${m.role}`}>
                    {m.role === 'assistant' && <div className="msg-avatar message-avatar"><BotIcon /></div>}
                    <div className="msg-bubble message-content">
                      {/* Triage level indicator */}
                      {m.role === 'assistant' && m.triage?.level && m.triage.level !== 'self_care' && (
                        <div className="message-triage-badge" style={{ borderLeftColor: m.triage.color }}>
                          <ShieldIcon />
                          <span>{m.triage.label}</span>
                          {m.triage.detected_condition && <span className="triage-condition">• {m.triage.detected_condition}</span>}
                        </div>
                      )}
                      
                      {/* Mental Health indicator for message */}
                      {m.role === 'assistant' && m.mentalHealth?.detected && (
                        <div className={`message-mh-indicator ${m.mentalHealth.is_crisis ? 'crisis' : m.mentalHealth.severity}`}>
                          <HeartHandIcon />
                          <span>{m.mentalHealth.is_crisis ? 'Crisis Support Activated' : 'Mental Health Support'}</span>
                      </div>
                    )}
                    
                    {/* Formatted message content */}
                    {m.role === 'assistant' ? (
                      <FormattedMessage 
                        text={m.text} 
                        triage={m.triage} 
                        medications={m.medications}
                        mentalHealth={m.mentalHealth}
                      />
                    ) : (
                      <div className="user-message-text">
                        {m.image && <img src={m.image} alt="Uploaded" className="user-message-image" />}
                        {m.text && <span>{m.text}</span>}
                        {!m.image && !m.text && <span>​</span>}
                      </div>
                    )}
                    
                    <div className="message-footer">
                      <div className="message-time">{formatTime(m.time)}</div>
                      {m.role === 'assistant' && (
                        <button 
                          className="message-speak-btn"
                          onClick={() => speak(m.text)}
                          title="Read aloud"
                        >
                          <VolumeIcon />
                        </button>
                      )}
                    </div>
                  </div>
                  {m.role === 'user' && (
                    <div className="msg-avatar message-avatar user-profile-avatar">
                      {authUser?.picture ? (
                        <img src={authUser.picture} alt="" className="user-msg-pic" referrerPolicy="no-referrer" />
                      ) : (
                        <UserIcon />
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
            {loading && (
              <div className="premium-msg message assistant">
                <div className="msg-avatar message-avatar lottie-avatar">
                  <dotlottie-wc 
                    src="https://lottie.host/534fef36-80e8-4072-a726-2afecbe9467b/8J3QDVdUdW.lottie" 
                    style={{ width: '36px', height: '36px' }}
                    autoplay 
                    loop
                  />
                </div>
                <div className="premium-typing typing-indicator">
                  <span></span><span></span><span></span>
                  <button className="cancel-btn" onClick={cancelRequest} title="Cancel request">
                    <StopCircleIcon /> Cancel
                  </button>
                </div>
              </div>
            )}
            <div ref={chatEndRef}></div>
            </div>
          </div>
          
          {/* Compact Input Area - All controls inline */}
          <div className="premium-input-area">
            <input type="file" ref={imageInputRef} accept="image/*" onChange={handleImageSelect} style={{ display: 'none' }} />
            <div className="premium-input-wrapper">
              <div className="inline-actions">
                <button className={`inline-btn ${isListening ? 'active' : ''}`} onClick={toggleListening} title="Voice input">
                  <MicIcon />
                </button>
                <button className="inline-btn" onClick={() => imageInputRef.current?.click()} title="Camera">
                  <CameraIcon />
                </button>
                <button className="inline-btn" onClick={() => setShowPrescription(true)} title="Prescription">
                  <ClipboardMedicalIcon size={16} />
                </button>
                <button className="inline-btn" onClick={() => setShowBodySelector(true)} title="Body map">
                  <BodyIcon size={16} color="#fff" />
                </button>
                <button className="inline-btn" onClick={() => setShowSpecialistFinder(true)} title="Find doctor">
                  <StethoscopeIcon size={16} />
                </button>
                <button className={`inline-btn ${showVitals ? 'active' : ''}`} onClick={fetchVitals} title="Watch vitals">
                  <HeartPulseIcon size={16} />
                </button>
                <button className={`inline-btn ${voiceEnabled ? 'active' : ''}`} onClick={() => isSpeaking ? stopSpeaking() : setVoiceEnabled(!voiceEnabled)} title="TTS">
                  {voiceEnabled ? <VolumeIcon /> : <VolumeOffIcon />}
                </button>
              </div>
              <input 
                type="text" 
                className="input-field" 
                value={input} 
                onChange={e => setInput(e.target.value)} 
                onKeyDown={e => e.key === 'Enter' && sendMsg()} 
                placeholder={isListening ? '🎤 Listening...' : 'Describe your symptoms...'} 
                disabled={loading} 
              />
              {isSpeaking && (
                <button className="p-action-btn stop" onClick={stopSpeaking} title="Stop speaking">
                  <StopIcon />
                </button>
              )}
              {loading ? (
                <button className="p-action-btn cancel-req" onClick={cancelRequest} title="Cancel request">
                  <StopCircleIcon />
                </button>
              ) : (
                <motion.button 
                  className="p-action-btn send" 
                  onClick={() => sendMsg()} 
                  disabled={!input.trim()}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <SendIcon />
                </motion.button>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
      <div className="premium-chat-footer">
        <p>For informational purposes only. Consult a healthcare professional.</p>
      </div>

      {/* Body Selector Modal */}
      <AnimatePresence>
        {showBodySelector && (
          <BodySelector
            onSelectSymptoms={handleBodyPartsSelected}
            onClose={() => setShowBodySelector(false)}
            language={detectedLang || language}
          />
        )}
      </AnimatePresence>

      {/* Specialist Finder Modal - Find nearby doctors & online consultation */}
      <AnimatePresence>
        {showSpecialistFinder && (
          <SpecialistFinder
            symptoms={detectedSymptoms}
            urgency={urgencyLevel}
            diagnoses={diagnoses}
            language={detectedLang || language}
            onClose={() => setShowSpecialistFinder(false)}
          />
        )}
      </AnimatePresence>

      {/* Prescription Analyzer — Full-screen page overlay */}
      {showPrescription && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 9999, background: '#0a0e1a', overflowY: 'auto' }}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => e.preventDefault()}
        >
          <PrescriptionPage onBack={() => setShowPrescription(false)} />
        </div>
      )}

      {/* Condition Details Modal - Shows detailed info when clicking a diagnosis */}
      <AnimatePresence>
        {showConditionDetails && selectedCondition && (
          <motion.div 
            className="condition-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowConditionDetails(false)}
          >
            <motion.div 
              className="condition-modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="condition-modal-header">
                <div className="condition-modal-title">
                  <h3>{selectedCondition.condition}</h3>
                </div>
                <button 
                  className="condition-modal-close"
                  onClick={() => setShowConditionDetails(false)}
                >
                  ✕
                </button>
              </div>
              
              <div className="condition-modal-confidence">
                <div className="confidence-label">Likelihood</div>
                <div className="confidence-bar-container">
                  <div 
                    className="confidence-bar-fill"
                    style={{ 
                      width: `${Math.round(selectedCondition.confidence * 100)}%`,
                      background: selectedCondition.confidence > 0.7 ? '#00d4aa' 
                                : selectedCondition.confidence > 0.5 ? '#fbbf24' : '#60a5fa'
                    }}
                  />
                </div>
                <span className="confidence-percent">{Math.round(selectedCondition.confidence * 100)}%</span>
              </div>

              {selectedCondition.urgency && (
                <div className={`condition-urgency urgency-${selectedCondition.urgency}`}>
                  {selectedCondition.urgency === 'emergency' && 'Emergency - Seek immediate care'}
                  {selectedCondition.urgency === 'urgent' && 'Urgent - See doctor within 24 hours'}
                  {selectedCondition.urgency === 'doctor_soon' && 'See a doctor within a few days'}
                  {selectedCondition.urgency === 'routine' && 'Routine - Schedule when convenient'}
                  {selectedCondition.urgency === 'self_care' && 'Self-care - Can manage at home'}
                </div>
              )}

              <div className="condition-modal-content">
                {conditionDetailsLoading ? (
                  <div className="condition-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading details...</p>
                  </div>
                ) : selectedCondition.detailedInfo ? (
                  <div className="condition-details-formatted">
                    {(() => {
                      // Parse the AI response into sections
                      const text = selectedCondition.detailedInfo
                      const sections = []
                      
                      // Extract sections with **header:** pattern
                      const whatMatch = text.match(/\*\*What it is[:\*]*\*?\*?\s*(.+?)(?=\*\*|$)/is)
                      const causesMatch = text.match(/\*\*Common causes[:\*]*\*?\*?\s*(.+?)(?=\*\*|$)/is)
                      const remediesMatch = text.match(/\*\*Home remedies[:\*]*\*?\*?\s*(.+?)(?=\*\*|$)/is)
                      const doctorMatch = text.match(/\*\*When to see[:\*]*\*?\*?\s*(.+?)(?=\*\*|$)/is)
                      
                      return (
                        <div className="condition-info-grid">
                          {whatMatch && (
                            <div className="info-section">
                              <div className="info-header">What is it?</div>
                              <p>{whatMatch[1].replace(/\*\*/g, '').trim()}</p>
                            </div>
                          )}
                          {causesMatch && (
                            <div className="info-section">
                              <div className="info-header">Common Causes</div>
                              <p>{causesMatch[1].replace(/\*\*/g, '').trim()}</p>
                            </div>
                          )}
                          {remediesMatch && (
                            <div className="info-section">
                              <div className="info-header">Home Care</div>
                              <p>{remediesMatch[1].replace(/\*\*/g, '').trim()}</p>
                            </div>
                          )}
                          {doctorMatch && (
                            <div className="info-section warning">
                              <div className="info-header">When to See a Doctor</div>
                              <p>{doctorMatch[1].replace(/\*\*/g, '').trim()}</p>
                            </div>
                          )}
                          {!whatMatch && !causesMatch && !remediesMatch && !doctorMatch && (
                            <div className="info-section">
                              <p>{text.replace(/\*\*/g, '').trim()}</p>
                            </div>
                          )}
                        </div>
                      )
                    })()}
                  </div>
                ) : (
                  <div className="condition-basic-info">
                    <p>{selectedCondition.description}</p>
                    {selectedCondition.specialist && (
                      <div className="condition-specialist">
                        <strong>Recommended Specialist:</strong> {selectedCondition.specialist}
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="condition-modal-actions">
                <button 
                  className="condition-action-btn primary"
                  onClick={() => { 
                    setShowSpecialistFinder(true); 
                    setShowConditionDetails(false); 
                  }}
                >
                  Find {selectedCondition.specialist || 'Doctor'}
                </button>
                <button 
                  className="condition-action-btn secondary"
                  onClick={() => setShowConditionDetails(false)}
                >
                  Close
                </button>
              </div>

              <div className="condition-disclaimer">
                This is AI-generated information for educational purposes. Always consult a healthcare professional for proper diagnosis and treatment.
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Symptom Details Modal */}
      <AnimatePresence>
        {showSymptomDetails && selectedSymptom && (
          <motion.div 
            className="symptom-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowSymptomDetails(false)}
          >
            <motion.div 
              className="symptom-modal"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="symptom-modal-header">
                <h3>{getSymptomInfo(selectedSymptom, language).name}</h3>
                <button 
                  className="symptom-modal-close"
                  onClick={() => setShowSymptomDetails(false)}
                >
                  <XIcon />
                </button>
              </div>
              <div className="symptom-modal-content">
                <div className="symptom-info-section">
                  <div className="symptom-info-icon">📋</div>
                  <div>
                    <h4>{language === 'en' ? 'Description' : language === 'hi' ? 'विवरण' : language === 'ta' ? 'விளக்கம்' : language === 'te' ? 'వివరణ' : 'Description'}</h4>
                    <p>{getSymptomInfo(selectedSymptom, language).description}</p>
                  </div>
                </div>
                <div className="symptom-info-section">
                  <div className="symptom-info-icon">🔍</div>
                  <div>
                    <h4>{language === 'en' ? 'Common Causes' : language === 'hi' ? 'सामान्य कारण' : language === 'ta' ? 'பொதுவான காரணங்கள்' : language === 'te' ? 'సాధారణ కారణాలు' : 'Causes'}</h4>
                    <p>{getSymptomInfo(selectedSymptom, language).causes}</p>
                  </div>
                </div>
                <div className="symptom-info-section">
                  <div className="symptom-info-icon">🏠</div>
                  <div>
                    <h4>{language === 'en' ? 'Home Remedies' : language === 'hi' ? 'घरेलू उपचार' : language === 'ta' ? 'வீட்டு வைத்தியம்' : language === 'te' ? 'ఇంటి నివారణలు' : 'Remedies'}</h4>
                    <p>{getSymptomInfo(selectedSymptom, language).homeRemedies}</p>
                  </div>
                </div>
                <div className="symptom-info-section warning">
                  <div className="symptom-info-icon">⚠️</div>
                  <div>
                    <h4>{language === 'en' ? 'When to See a Doctor' : language === 'hi' ? 'डॉक्टर को कब दिखाएं' : language === 'ta' ? 'மருத்துவரை எப்போது பார்க்க வேண்டும்' : language === 'te' ? 'వైద్యుడిని ఎప్పుడు సంప్రదించాలి' : 'See Doctor'}</h4>
                    <p>{getSymptomInfo(selectedSymptom, language).whenToSeeDoctor}</p>
                  </div>
                </div>
              </div>
              <div className="symptom-modal-footer">
                <button 
                  className="symptom-modal-btn primary"
                  onClick={() => {
                    setInput(`Tell me more about ${selectedSymptom}`)
                    setShowSymptomDetails(false)
                    setTimeout(() => sendMsg(), 100)
                  }}
                >
                  {language === 'en' ? 'Ask AI for More Details' : language === 'hi' ? 'AI से और जानकारी पूछें' : 'Ask AI'}
                </button>
                <button 
                  className="symptom-modal-btn secondary"
                  onClick={() => setShowSymptomDetails(false)}
                >
                  {language === 'en' ? 'Close' : language === 'hi' ? 'बंद करें' : 'Close'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

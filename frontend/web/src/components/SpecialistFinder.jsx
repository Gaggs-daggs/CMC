/**
 * 🏥 SPECIALIST FINDER COMPONENT - PREMIUM VERSION
 * =================================================
 * Embedded Google Maps for finding nearby specialists
 * Online consultation links & emergency services
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Premium Icons
const Icons = {
  Hospital: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 21h18M9 8h6M12 8v6M4 21V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v13M9 21v-6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v6"/>
    </svg>
  ),
  Location: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
    </svg>
  ),
  Phone: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
    </svg>
  ),
  Video: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
    </svg>
  ),
  Alert: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
  Heart: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
    </svg>
  ),
  Brain: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>
      <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>
    </svg>
  ),
  Bone: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18.6 9.82c-.52-.21-1.15-.25-1.54.15l-7.07 7.06c-.39.39-.36 1.03-.15 1.54.12.3.16.6.16.92a3 3 0 1 1-5.46 1.7 3 3 0 0 1 1.7-5.46c.31 0 .62.04.92.16.51.21 1.15.24 1.54-.15l7.07-7.06c.39-.39.36-1.03.15-1.54a2.3 2.3 0 0 1-.16-.92 3 3 0 1 1 5.46-1.7 3 3 0 0 1-1.7 5.46c-.31 0-.62-.04-.92-.16Z"/>
    </svg>
  ),
  Eye: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
    </svg>
  ),
  Stethoscope: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/>
      <path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/>
    </svg>
  ),
  Baby: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 12h.01M15 12h.01M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/>
      <path d="M19 6.3a9 9 0 0 1 1.8 3.9 2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1"/>
    </svg>
  ),
  Ambulance: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 10H6"/><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/>
      <path d="M19 18h2a1 1 0 0 0 1-1v-3.28a1 1 0 0 0-.684-.948l-1.923-.641a1 1 0 0 1-.578-.502l-1.539-3.076A1 1 0 0 0 16.382 8H14"/>
      <path d="M8 8v4"/><path d="M9 18h6"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>
    </svg>
  ),
  Pill: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/>
    </svg>
  ),
  Tooth: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 5.5c-1.5-1-4-1.5-5 .5-1 2 0 4 1 6s1 4 0 6c-.5 1 .5 2 1.5 2 1.5 0 2-1 3-3 .5-1 1.5-1 2 0 1 2 1.5 3 3 3 1 0 2-1 1.5-2-1-2-1-4 0-6s2-4 1-6c-1-2-3.5-1.5-5-.5l-1.5 1-.5-1Z"/>
    </svg>
  ),
  Lungs: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6.081 20C2.661 20 .064 16.455.718 13.099a26.5 26.5 0 0 1 3.768-9.025C5.392 2.77 6.108 2 7.016 2c1.822 0 2.984 2.326 2.984 5v11a2 2 0 0 1-2 2H6.081Z"/>
      <path d="M17.92 20c3.42 0 6.017-3.545 5.363-6.901a26.5 26.5 0 0 0-3.769-9.025C18.608 2.77 17.892 2 16.984 2c-1.822 0-2.984 2.326-2.984 5v11a2 2 0 0 0 2 2h1.919Z"/>
    </svg>
  ),
  Ear: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 8.5a6.5 6.5 0 1 1 13 0c0 6-6 6-6 10a3.5 3.5 0 1 1-7 0"/>
      <path d="M15 8.5a2.5 2.5 0 0 0-5 0v1a2 2 0 1 1 0 4"/>
    </svg>
  ),
  Stomach: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 2s3 2 3 7-3 7-3 7M5 9c0-2 1-3 2-3s2 1.5 2 3c0 2.5-2 3-2 5 0 1.5 1 2.5 2 2.5"/>
      <path d="M17.5 9.5C17.5 13 15 15 12 15s-5.5-2-5.5-5.5S9 4 12 4s5.5 2.5 5.5 5.5Z"/>
      <path d="M12 15v4M10 22h4"/>
    </svg>
  ),
  MapPin: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
    </svg>
  ),
  Close: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  ),
  ExternalLink: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
  ),
  Clock: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
    </svg>
  ),
  Check: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>
  ),
  Star: () => (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
    </svg>
  ),
  Refresh: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
    </svg>
  ),
};

// Specialist configurations with icons and colors
const SPECIALISTS = [
  { id: 'general', name: 'General Physician', icon: Icons.Stethoscope, color: '#00c896', search: 'general physician clinic' },
  { id: 'cardio', name: 'Cardiologist', icon: Icons.Heart, color: '#ef4444', search: 'cardiologist heart specialist' },
  { id: 'neuro', name: 'Neurologist', icon: Icons.Brain, color: '#8b5cf6', search: 'neurologist brain specialist' },
  { id: 'ortho', name: 'Orthopedic', icon: Icons.Bone, color: '#f59e0b', search: 'orthopedic bone doctor' },
  { id: 'eye', name: 'Ophthalmologist', icon: Icons.Eye, color: '#3b82f6', search: 'eye specialist ophthalmologist' },
  { id: 'ent', name: 'ENT Specialist', icon: Icons.Ear, color: '#ec4899', search: 'ent ear nose throat' },
  { id: 'gastro', name: 'Gastroenterologist', icon: Icons.Stomach, color: '#10b981', search: 'gastroenterologist stomach' },
  { id: 'pulmo', name: 'Pulmonologist', icon: Icons.Lungs, color: '#06b6d4', search: 'pulmonologist lung specialist' },
  { id: 'dentist', name: 'Dentist', icon: Icons.Tooth, color: '#f472b6', search: 'dentist dental clinic' },
  { id: 'pediatric', name: 'Pediatrician', icon: Icons.Baby, color: '#a855f7', search: 'pediatrician child specialist' },
  { id: 'derma', name: 'Dermatologist', icon: Icons.Pill, color: '#14b8a6', search: 'dermatologist skin specialist' },
  { id: 'emergency', name: 'Emergency', icon: Icons.Ambulance, color: '#dc2626', search: 'emergency hospital 24 hours' },
];

// Online consultation platforms with better data
const TELEMEDICINE = [
  {
    name: 'Practo',
    url: 'https://www.practo.com/consult',
    color: '#ff6f61',
    rating: 4.5,
    consultations: '50M+',
    price: '₹199',
    features: ['Video Call', 'Chat', 'E-Prescription'],
    waitTime: '5 min'
  },
  {
    name: 'Apollo 24|7',
    url: 'https://www.apollo247.com/specialties',
    color: '#1a73e8',
    rating: 4.6,
    consultations: '20M+',
    price: '₹299',
    features: ['24/7 Available', 'Lab Tests', 'Medicine Delivery'],
    waitTime: '10 min'
  },
  {
    name: 'Tata 1mg',
    url: 'https://www.1mg.com/online-doctor-consultation',
    color: '#ff4081',
    rating: 4.4,
    consultations: '30M+',
    price: '₹149',
    features: ['Instant Consult', 'Free Follow-up', 'Health Records'],
    waitTime: '3 min'
  },
  {
    name: 'MFine',
    url: 'https://www.mfine.co/',
    color: '#7c3aed',
    rating: 4.3,
    consultations: '10M+',
    price: '₹199',
    features: ['AI Symptom Check', 'Specialist Match', 'Digital Reports'],
    waitTime: '5 min'
  },
];

// Emergency services
const EMERGENCY_SERVICES = [
  { name: 'Ambulance', number: '108', icon: '🚑', color: '#dc2626', desc: 'Medical Emergency' },
  { name: 'Police', number: '100', icon: '👮', color: '#3b82f6', desc: 'Police Emergency' },
  { name: 'Fire', number: '101', icon: '🚒', color: '#f97316', desc: 'Fire Brigade' },
  { name: 'Women', number: '181', icon: '👩', color: '#ec4899', desc: 'Women Helpline' },
  { name: 'Child', number: '1098', icon: '👶', color: '#8b5cf6', desc: 'Child Helpline' },
  { name: 'Mental Health', number: '9152987821', icon: '🧠', color: '#10b981', desc: 'iCALL Support' },
];

const SpecialistFinder = ({ 
  symptoms = [], 
  urgency = 'low', 
  diagnoses = [], 
  language = 'en',
  onClose 
}) => {
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(true);
  const [activeTab, setActiveTab] = useState(urgency === 'emergency' ? 'emergency' : 'map');
  const [selectedSpecialist, setSelectedSpecialist] = useState(SPECIALISTS[0]);
  const [mapUrl, setMapUrl] = useState('');

  // Get user location on mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
          setIsLoadingLocation(false);
        },
        (err) => {
          setLocationError('Location access denied. Using default search.');
          setIsLoadingLocation(false);
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    } else {
      setLocationError('Geolocation not supported');
      setIsLoadingLocation(false);
    }
  }, []);

  // Update map URL when location or specialist changes
  useEffect(() => {
    if (selectedSpecialist) {
      const query = encodeURIComponent(selectedSpecialist.search + ' near me');
      if (userLocation) {
        // Use OpenStreetMap embed instead of Google Maps (no API key needed)
        const osmUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${userLocation.lng - 0.05}%2C${userLocation.lat - 0.05}%2C${userLocation.lng + 0.05}%2C${userLocation.lat + 0.05}&layer=mapnik&marker=${userLocation.lat}%2C${userLocation.lng}`;
        setMapUrl(osmUrl);
      } else {
        // Default to a general map view
        setMapUrl('https://www.openstreetmap.org/export/embed.html?bbox=77.5%2C12.9%2C77.7%2C13.1&layer=mapnik');
      }
    }
  }, [userLocation, selectedSpecialist]);

  // Determine recommended specialist from symptoms
  useEffect(() => {
    const allTerms = [...symptoms, ...diagnoses.map(d => d.name || d)].join(' ').toLowerCase();
    
    if (/heart|chest|cardio|palpitation/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'cardio'));
    } else if (/head|migraine|brain|dizz|seizure/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'neuro'));
    } else if (/bone|joint|back|knee|fracture|spine/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'ortho'));
    } else if (/eye|vision|sight/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'eye'));
    } else if (/ear|throat|nose|sinus/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'ent'));
    } else if (/stomach|abdomen|digest|liver/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'gastro'));
    } else if (/breath|lung|cough|asthma/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'pulmo'));
    } else if (/tooth|dental|gum/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'dentist'));
    } else if (/child|baby|infant/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'pediatric'));
    } else if (/skin|rash|allergy/.test(allTerms)) {
      setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'derma'));
    }
  }, [symptoms, diagnoses]);

  const openInGoogleMaps = () => {
    const query = encodeURIComponent(selectedSpecialist.search);
    if (userLocation) {
      window.open(`https://www.google.com/maps/search/${query}/@${userLocation.lat},${userLocation.lng},14z`, '_blank');
    } else {
      window.open(`https://www.google.com/maps/search/${query}`, '_blank');
    }
  };

  const refreshLocation = () => {
    setIsLoadingLocation(true);
    setLocationError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setIsLoadingLocation(false);
      },
      () => {
        setLocationError('Could not get location');
        setIsLoadingLocation(false);
      },
      { enableHighAccuracy: true }
    );
  };

  return (
    <motion.div
      className="sf-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="sf-modal"
        initial={{ scale: 0.9, y: 30 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 30 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sf-header">
          <div className="sf-header-title">
            <div className="sf-header-icon">
              <Icons.Hospital />
            </div>
            <div>
              <h2>Find Healthcare</h2>
              <p>Specialists, Online Doctors & Emergency</p>
            </div>
          </div>
          <button className="sf-close-btn" onClick={onClose} aria-label="Close">
            <Icons.Close />
          </button>
        </div>

        {/* Urgency Alert */}
        {urgency === 'emergency' && (
          <div className="sf-urgency-alert emergency">
            <Icons.Alert />
            <span>Emergency detected! Seek immediate medical help</span>
          </div>
        )}
        {urgency === 'high' && (
          <div className="sf-urgency-alert high">
            <Icons.Alert />
            <span>High urgency - Consider consulting a doctor soon</span>
          </div>
        )}

        {/* Tabs */}
        <div className="sf-tabs" role="tablist">
          <button 
            role="tab"
            aria-selected={activeTab === 'map'}
            className={`sf-tab ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            <Icons.Location />
            <span>Nearby</span>
          </button>
          <button 
            role="tab"
            aria-selected={activeTab === 'online'}
            className={`sf-tab ${activeTab === 'online' ? 'active' : ''}`}
            onClick={() => setActiveTab('online')}
          >
            <Icons.Video />
            <span>Online</span>
          </button>
          <button 
            role="tab"
            aria-selected={activeTab === 'emergency'}
            className={`sf-tab ${activeTab === 'emergency' ? 'active' : ''}`}
            onClick={() => setActiveTab('emergency')}
          >
            <Icons.Ambulance />
            <span>Emergency</span>
          </button>
        </div>

        {/* Content */}
        <div className="sf-content">
          {/* Map Tab */}
          {activeTab === 'map' && (
            <div className="sf-map-tab">
              {/* Specialist Selector */}
              <div className="sf-specialist-selector">
                <div className="sf-selector-label">Select Specialist:</div>
                <div className="sf-specialist-grid">
                  {SPECIALISTS.map((spec) => {
                    const IconComponent = spec.icon;
                    return (
                      <button
                        key={spec.id}
                        className={`sf-spec-btn ${selectedSpecialist?.id === spec.id ? 'active' : ''}`}
                        onClick={() => setSelectedSpecialist(spec)}
                        style={{ '--spec-color': spec.color }}
                        aria-label={spec.name}
                      >
                        <div className="sf-spec-icon">
                          <IconComponent />
                        </div>
                        <span className="sf-spec-name">{spec.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Location Status */}
              <div className="sf-location-bar">
                <div className="sf-location-status">
                  <Icons.MapPin />
                  {isLoadingLocation ? (
                    <span>Getting your location...</span>
                  ) : locationError ? (
                    <span className="sf-location-error">{locationError}</span>
                  ) : (
                    <span className="sf-location-success">📍 Location enabled ({userLocation?.lat.toFixed(4)}, {userLocation?.lng.toFixed(4)})</span>
                  )}
                </div>
                <button className="sf-refresh-btn" onClick={refreshLocation} aria-label="Refresh location">
                  <Icons.Refresh />
                </button>
              </div>

              {/* Embedded Map */}
              <div className="sf-map-container">
                {mapUrl ? (
                  <iframe
                    title="Nearby Specialists Map"
                    src={mapUrl}
                    className="sf-map-iframe"
                    allowFullScreen
                    loading="lazy"
                    referrerPolicy="no-referrer-when-downgrade"
                  />
                ) : (
                  <div className="sf-map-loading">
                    <div className="sf-spinner"></div>
                    <span>Loading map...</span>
                  </div>
                )}
                
                {/* Map Overlay with info */}
                <div className="sf-map-overlay">
                  <div className="sf-map-selected">
                    {selectedSpecialist && (
                      <>
                        <span style={{ color: selectedSpecialist.color }}>●</span>
                        <span>Searching: {selectedSpecialist.name}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Open in Google Maps Button */}
              <button className="sf-open-maps-btn" onClick={openInGoogleMaps}>
                <Icons.ExternalLink />
                <span>🗺️ Search in Google Maps</span>
              </button>
            </div>
          )}

          {/* Online Consultation Tab */}
          {activeTab === 'online' && (
            <div className="sf-online-tab">
              <p className="sf-online-intro">
                🩺 Consult verified doctors from home via video call
              </p>
              <div className="sf-tele-grid">
                {TELEMEDICINE.map((platform) => (
                  <motion.a
                    key={platform.name}
                    href={platform.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sf-tele-card"
                    style={{ '--platform-color': platform.color }}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="sf-tele-header">
                      <div className="sf-tele-logo" style={{ background: platform.color }}>
                        {platform.name.charAt(0)}
                      </div>
                      <div className="sf-tele-info">
                        <h4>{platform.name}</h4>
                        <div className="sf-tele-rating">
                          <Icons.Star />
                          <span>{platform.rating}</span>
                          <span className="sf-tele-consults">• {platform.consultations} consultations</span>
                        </div>
                      </div>
                    </div>
                    <div className="sf-tele-features">
                      {platform.features.map((f, i) => (
                        <span key={i} className="sf-feature">
                          <Icons.Check /> {f}
                        </span>
                      ))}
                    </div>
                    <div className="sf-tele-footer">
                      <div className="sf-tele-price">From {platform.price}</div>
                      <div className="sf-tele-wait">
                        <Icons.Clock /> ~{platform.waitTime} wait
                      </div>
                    </div>
                    <div className="sf-tele-cta">
                      Book Now <Icons.ExternalLink />
                    </div>
                  </motion.a>
                ))}
              </div>
            </div>
          )}

          {/* Emergency Tab */}
          {activeTab === 'emergency' && (
            <div className="sf-emergency-tab">
              <div className="sf-emergency-alert">
                <Icons.Alert />
                <p>For life-threatening emergencies, call immediately!</p>
              </div>
              <div className="sf-emergency-grid">
                {EMERGENCY_SERVICES.map((service) => (
                  <a
                    key={service.name}
                    href={`tel:${service.number}`}
                    className="sf-emergency-card"
                    style={{ '--emerg-color': service.color }}
                  >
                    <div className="sf-emerg-icon">{service.icon}</div>
                    <div className="sf-emerg-info">
                      <span className="sf-emerg-name">{service.name}</span>
                      <span className="sf-emerg-desc">{service.desc}</span>
                    </div>
                    <div className="sf-emerg-number">{service.number}</div>
                  </a>
                ))}
              </div>
              <button 
                className="sf-find-hospital-btn"
                onClick={() => {
                  setSelectedSpecialist(SPECIALISTS.find(s => s.id === 'emergency'));
                  setActiveTab('map');
                }}
              >
                <Icons.Hospital />
                <span>Find Nearest Emergency Hospital</span>
              </button>
            </div>
          )}
        </div>
      </motion.div>

      <style>{`
        .sf-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.85);
          backdrop-filter: blur(12px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10000;
          padding: 1rem;
        }

        .sf-modal {
          background: linear-gradient(145deg, #1e1e2e 0%, #12121a 100%);
          border-radius: 24px;
          width: 100%;
          max-width: 800px;
          max-height: 90vh;
          overflow: hidden;
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 40px rgba(0, 200, 150, 0.1);
          display: flex;
          flex-direction: column;
        }

        .sf-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.25rem 1.5rem;
          background: rgba(0, 200, 150, 0.08);
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .sf-header-title {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .sf-header-icon {
          width: 48px;
          height: 48px;
          background: linear-gradient(135deg, #00c896 0%, #00a67c 100%);
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: 0 4px 15px rgba(0, 200, 150, 0.4);
        }

        .sf-header h2 {
          margin: 0;
          font-size: 1.3rem;
          font-weight: 700;
          color: #fff;
        }

        .sf-header p {
          margin: 0;
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.6);
        }

        .sf-close-btn {
          width: 40px;
          height: 40px;
          border: none;
          background: rgba(255, 255, 255, 0.08);
          border-radius: 12px;
          color: rgba(255, 255, 255, 0.7);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .sf-close-btn:hover {
          background: rgba(255, 100, 100, 0.2);
          color: #ff6b6b;
        }

        .sf-urgency-alert {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          padding: 0.85rem 1rem;
          font-weight: 600;
          font-size: 0.9rem;
        }

        .sf-urgency-alert.emergency {
          background: linear-gradient(90deg, #dc2626, #b91c1c);
          color: white;
          animation: pulse-bg 2s infinite;
        }

        .sf-urgency-alert.high {
          background: linear-gradient(90deg, #f59e0b, #d97706);
          color: white;
        }

        @keyframes pulse-bg {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.85; }
        }

        .sf-tabs {
          display: flex;
          background: rgba(0, 0, 0, 0.3);
          padding: 0.5rem;
          gap: 0.5rem;
        }

        .sf-tab {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.85rem 1rem;
          border: none;
          background: transparent;
          border-radius: 12px;
          color: rgba(255, 255, 255, 0.6);
          font-weight: 600;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .sf-tab:hover {
          background: rgba(255, 255, 255, 0.05);
          color: rgba(255, 255, 255, 0.9);
        }

        .sf-tab.active {
          background: linear-gradient(135deg, #00c896 0%, #00a67c 100%);
          color: white;
          box-shadow: 0 4px 15px rgba(0, 200, 150, 0.3);
        }

        .sf-content {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
        }

        .sf-content::-webkit-scrollbar {
          width: 6px;
        }

        .sf-content::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.15);
          border-radius: 3px;
        }

        /* Map Tab */
        .sf-map-tab {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .sf-selector-label {
          font-size: 0.85rem;
          color: rgba(255, 255, 255, 0.7);
          margin-bottom: 0.5rem;
          font-weight: 500;
        }

        .sf-specialist-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 0.5rem;
        }

        .sf-spec-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.4rem;
          padding: 0.75rem 0.5rem;
          border: 1px solid rgba(255, 255, 255, 0.1);
          background: rgba(255, 255, 255, 0.03);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s;
          color: rgba(255, 255, 255, 0.8);
        }

        .sf-spec-btn:hover {
          background: rgba(255, 255, 255, 0.08);
          border-color: var(--spec-color);
        }

        .sf-spec-btn.active {
          background: rgba(0, 200, 150, 0.15);
          border-color: #00c896;
          color: #00c896;
        }

        .sf-spec-icon {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.08);
          border-radius: 10px;
          transition: all 0.2s;
        }

        .sf-spec-btn:hover .sf-spec-icon,
        .sf-spec-btn.active .sf-spec-icon {
          background: var(--spec-color);
          color: white;
        }

        .sf-spec-name {
          font-size: 0.7rem;
          text-align: center;
          line-height: 1.2;
          font-weight: 500;
        }

        .sf-location-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.75rem 1rem;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
        }

        .sf-location-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: rgba(255, 255, 255, 0.7);
        }

        .sf-location-status svg {
          color: #00c896;
        }

        .sf-location-success {
          color: #00c896;
        }

        .sf-location-error {
          color: #f59e0b;
        }

        .sf-refresh-btn {
          width: 36px;
          height: 36px;
          border: none;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          color: rgba(255, 255, 255, 0.7);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .sf-refresh-btn:hover {
          background: rgba(0, 200, 150, 0.2);
          color: #00c896;
        }

        .sf-map-container {
          position: relative;
          width: 100%;
          height: 300px;
          border-radius: 16px;
          overflow: hidden;
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .sf-map-iframe {
          width: 100%;
          height: 100%;
          border: none;
        }

        .sf-map-overlay {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          padding: 0.75rem;
          background: linear-gradient(transparent, rgba(0,0,0,0.8));
        }

        .sf-map-selected {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
          color: white;
          font-weight: 500;
        }

        .sf-map-loading {
          width: 100%;
          height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          color: rgba(255, 255, 255, 0.6);
        }

        .sf-spinner {
          width: 40px;
          height: 40px;
          border: 3px solid rgba(0, 200, 150, 0.2);
          border-top-color: #00c896;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .sf-open-maps-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          width: 100%;
          padding: 1rem;
          background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%);
          border: none;
          border-radius: 14px;
          color: white;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
        }

        .sf-open-maps-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 25px rgba(66, 133, 244, 0.4);
        }

        /* Online Tab */
        .sf-online-tab {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .sf-online-intro {
          text-align: center;
          color: rgba(255, 255, 255, 0.7);
          margin: 0;
          font-size: 0.9rem;
        }

        .sf-tele-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
        }

        .sf-tele-card {
          display: flex;
          flex-direction: column;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          text-decoration: none;
          color: white;
          transition: all 0.2s;
        }

        .sf-tele-card:hover {
          border-color: var(--platform-color);
          background: rgba(255, 255, 255, 0.08);
        }

        .sf-tele-header {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
        }

        .sf-tele-logo {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.4rem;
          font-weight: 700;
          color: white;
        }

        .sf-tele-info h4 {
          margin: 0;
          font-size: 1rem;
          font-weight: 600;
        }

        .sf-tele-rating {
          display: flex;
          align-items: center;
          gap: 0.3rem;
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.6);
        }

        .sf-tele-rating svg {
          color: #fbbf24;
        }

        .sf-tele-consults {
          opacity: 0.6;
        }

        .sf-tele-features {
          display: flex;
          flex-wrap: wrap;
          gap: 0.4rem;
          margin-bottom: 0.75rem;
        }

        .sf-feature {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.7rem;
          padding: 0.25rem 0.5rem;
          background: rgba(0, 200, 150, 0.15);
          color: #00c896;
          border-radius: 6px;
        }

        .sf-tele-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.75rem;
          font-size: 0.8rem;
        }

        .sf-tele-price {
          font-weight: 600;
          color: #00c896;
        }

        .sf-tele-wait {
          display: flex;
          align-items: center;
          gap: 0.3rem;
          color: rgba(255, 255, 255, 0.6);
        }

        .sf-tele-cta {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.75rem;
          background: var(--platform-color);
          border-radius: 10px;
          font-weight: 600;
          font-size: 0.85rem;
        }

        /* Emergency Tab */
        .sf-emergency-tab {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .sf-emergency-alert {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          padding: 1rem;
          background: rgba(220, 38, 38, 0.15);
          border: 1px solid rgba(220, 38, 38, 0.3);
          border-radius: 14px;
          color: #fca5a5;
        }

        .sf-emergency-alert p {
          margin: 0;
          font-weight: 500;
        }

        .sf-emergency-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.75rem;
        }

        .sf-emergency-card {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 14px;
          text-decoration: none;
          color: white;
          transition: all 0.2s;
        }

        .sf-emergency-card:hover {
          background: rgba(255, 255, 255, 0.08);
          border-color: var(--emerg-color);
          transform: translateY(-2px);
        }

        .sf-emerg-icon {
          font-size: 2rem;
        }

        .sf-emerg-info {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .sf-emerg-name {
          font-weight: 600;
          font-size: 0.95rem;
        }

        .sf-emerg-desc {
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.5);
        }

        .sf-emerg-number {
          font-size: 1.1rem;
          font-weight: 700;
          padding: 0.5rem 0.75rem;
          background: var(--emerg-color);
          border-radius: 10px;
        }

        .sf-find-hospital-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          width: 100%;
          padding: 1rem;
          background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
          border: none;
          border-radius: 14px;
          color: white;
          font-weight: 600;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
        }

        .sf-find-hospital-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 25px rgba(220, 38, 38, 0.4);
        }

        /* Responsive */
        @media (max-width: 700px) {
          .sf-modal {
            max-height: 95vh;
            border-radius: 20px;
          }

          .sf-specialist-grid {
            grid-template-columns: repeat(3, 1fr);
          }

          .sf-tele-grid {
            grid-template-columns: 1fr;
          }

          .sf-emergency-grid {
            grid-template-columns: 1fr;
          }

          .sf-map-container {
            height: 250px;
          }

          .sf-tab span {
            display: none;
          }

          .sf-tab {
            padding: 0.75rem;
          }
        }

        @media (max-width: 500px) {
          .sf-specialist-grid {
            grid-template-columns: repeat(3, 1fr);
          }

          .sf-spec-name {
            font-size: 0.65rem;
          }

          .sf-header-title p {
            display: none;
          }
        }
      `}</style>
    </motion.div>
  );
};

export default SpecialistFinder;

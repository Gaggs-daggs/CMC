/**
 * 🫀 COMPREHENSIVE INTERACTIVE HUMAN BODY SELECTOR
 * =================================================
 * Detailed SVG body selector with 50+ clickable regions.
 * Includes muscles, joints, organs, and body parts.
 */

import React, { useState } from 'react';

// ULTRA-COMPREHENSIVE body regions with symptoms - 100+ parts
const BODY_REGIONS = {
  // ========== HEAD & SKULL ==========
  head: { label: "Head (Crown)", symptoms: ["headache at top of head", "crown pain"] },
  forehead: { label: "Forehead", symptoms: ["forehead pain", "tension headache", "sinus pressure"] },
  leftTemple: { label: "Left Temple", symptoms: ["left temple pain", "temporal headache"] },
  rightTemple: { label: "Right Temple", symptoms: ["right temple pain", "temporal headache"] },
  skullBack: { label: "Back of Head", symptoms: ["occipital pain", "back of head headache"] },
  
  // ========== FACE ==========
  leftEye: { label: "Left Eye", symptoms: ["left eye pain", "eye strain", "vision problems"] },
  rightEye: { label: "Right Eye", symptoms: ["right eye pain", "eye strain", "vision problems"] },
  leftEyebrow: { label: "Left Eyebrow", symptoms: ["left brow pain", "supraorbital pain"] },
  rightEyebrow: { label: "Right Eyebrow", symptoms: ["right brow pain", "supraorbital pain"] },
  nose: { label: "Nose", symptoms: ["nasal congestion", "sinus pain", "nosebleed"] },
  noseBridge: { label: "Nose Bridge", symptoms: ["nose bridge pain", "nasal bone pain"] },
  leftCheek: { label: "Left Cheek", symptoms: ["left cheek pain", "cheekbone pain"] },
  rightCheek: { label: "Right Cheek", symptoms: ["right cheek pain", "cheekbone pain"] },
  leftSinus: { label: "Left Sinus", symptoms: ["left sinus pain", "sinus pressure"] },
  rightSinus: { label: "Right Sinus", symptoms: ["right sinus pain", "sinus pressure"] },
  leftEar: { label: "Left Ear", symptoms: ["left ear pain", "ear infection", "hearing issues"] },
  rightEar: { label: "Right Ear", symptoms: ["right ear pain", "ear infection", "hearing issues"] },
  upperLip: { label: "Upper Lip", symptoms: ["upper lip pain", "lip numbness"] },
  lowerLip: { label: "Lower Lip", symptoms: ["lower lip pain", "cracked lips"] },
  mouth: { label: "Mouth", symptoms: ["mouth pain", "oral pain", "tongue pain"] },
  chin: { label: "Chin", symptoms: ["chin pain", "mentalis pain"] },
  leftJaw: { label: "Left Jaw", symptoms: ["left jaw pain", "TMJ left side"] },
  rightJaw: { label: "Right Jaw", symptoms: ["right jaw pain", "TMJ right side"] },
  jaw: { label: "Jaw (Center)", symptoms: ["jaw pain", "TMJ pain", "difficulty chewing"] },
  
  // ========== NECK & THROAT ==========
  neck: { label: "Neck (Front)", symptoms: ["neck pain", "stiff neck", "throat pain"] },
  neckLeft: { label: "Neck (Left Side)", symptoms: ["left neck pain", "left side stiffness"] },
  neckRight: { label: "Neck (Right Side)", symptoms: ["right neck pain", "right side stiffness"] },
  neckBack: { label: "Neck (Back)", symptoms: ["back of neck pain", "neck stiffness"] },
  throat: { label: "Throat", symptoms: ["sore throat", "difficulty swallowing", "hoarseness"] },
  thyroid: { label: "Thyroid Area", symptoms: ["thyroid pain", "neck swelling"] },
  adam: { label: "Adam's Apple", symptoms: ["larynx pain", "voice box pain"] },
  lymphNodesNeck: { label: "Neck Lymph Nodes", symptoms: ["swollen lymph nodes", "neck lumps"] },
  
  // ========== SHOULDERS ==========
  leftShoulder: { label: "Left Shoulder", symptoms: ["left shoulder pain", "frozen shoulder"] },
  rightShoulder: { label: "Right Shoulder", symptoms: ["right shoulder pain", "frozen shoulder"] },
  leftShoulderFront: { label: "Left Shoulder (Front)", symptoms: ["left anterior shoulder pain"] },
  rightShoulderFront: { label: "Right Shoulder (Front)", symptoms: ["right anterior shoulder pain"] },
  leftRotatorCuff: { label: "Left Rotator Cuff", symptoms: ["left rotator cuff pain", "shoulder injury"] },
  rightRotatorCuff: { label: "Right Rotator Cuff", symptoms: ["right rotator cuff pain", "shoulder injury"] },
  leftCollarbone: { label: "Left Collarbone", symptoms: ["left clavicle pain", "collarbone pain"] },
  rightCollarbone: { label: "Right Collarbone", symptoms: ["right clavicle pain", "collarbone pain"] },
  leftTrapezius: { label: "Left Trapezius", symptoms: ["left trap pain", "upper back tension"] },
  rightTrapezius: { label: "Right Trapezius", symptoms: ["right trap pain", "upper back tension"] },
  leftDeltoid: { label: "Left Deltoid", symptoms: ["left shoulder muscle pain"] },
  rightDeltoid: { label: "Right Deltoid", symptoms: ["right shoulder muscle pain"] },
  
  // ========== CHEST & TORSO FRONT ==========
  leftPec: { label: "Left Pectoral", symptoms: ["left chest muscle pain"] },
  rightPec: { label: "Right Pectoral", symptoms: ["right chest muscle pain"] },
  sternum: { label: "Sternum/Breastbone", symptoms: ["sternum pain", "chest bone pain"] },
  heart: { label: "Heart Area", symptoms: ["heart pain", "chest tightness", "palpitations"] },
  leftChest: { label: "Left Chest", symptoms: ["left chest pain", "left breast pain"] },
  rightChest: { label: "Right Chest", symptoms: ["right chest pain", "right breast pain"] },
  leftRibs: { label: "Left Ribs (Front)", symptoms: ["left rib pain", "side pain"] },
  rightRibs: { label: "Right Ribs (Front)", symptoms: ["right rib pain", "side pain"] },
  leftRibsSide: { label: "Left Ribs (Side)", symptoms: ["left lateral rib pain"] },
  rightRibsSide: { label: "Right Ribs (Side)", symptoms: ["right lateral rib pain"] },
  leftArmpit: { label: "Left Armpit", symptoms: ["left armpit pain", "axillary pain"] },
  rightArmpit: { label: "Right Armpit", symptoms: ["right armpit pain", "axillary pain"] },
  
  // ========== ABDOMEN & ORGANS ==========
  upperAbdomen: { label: "Upper Abdomen", symptoms: ["upper stomach pain", "indigestion"] },
  epigastric: { label: "Epigastric Area", symptoms: ["epigastric pain", "upper central pain"] },
  liver: { label: "Liver Area", symptoms: ["liver pain", "right upper quadrant pain"] },
  gallbladder: { label: "Gallbladder Area", symptoms: ["gallbladder pain", "biliary pain"] },
  spleen: { label: "Spleen Area", symptoms: ["spleen pain", "left upper quadrant pain"] },
  stomach: { label: "Stomach", symptoms: ["stomach pain", "nausea", "gastritis"] },
  pancreas: { label: "Pancreas Area", symptoms: ["pancreas pain", "central abdominal pain"] },
  navel: { label: "Navel/Belly Button", symptoms: ["umbilical pain", "belly button pain"] },
  leftAbdomen: { label: "Left Abdomen", symptoms: ["left side abdominal pain"] },
  rightAbdomen: { label: "Right Abdomen", symptoms: ["right side abdominal pain"] },
  appendix: { label: "Appendix Area", symptoms: ["appendix pain", "right lower quadrant pain"] },
  lowerAbdomen: { label: "Lower Abdomen", symptoms: ["lower abdominal pain", "bladder pain"] },
  leftLowerAbdomen: { label: "Left Lower Abdomen", symptoms: ["left lower quadrant pain"] },
  rightLowerAbdomen: { label: "Right Lower Abdomen", symptoms: ["right lower quadrant pain"] },
  bladder: { label: "Bladder Area", symptoms: ["bladder pain", "urinary pain"] },
  
  // ========== PELVIS & HIP ==========
  pelvis: { label: "Pelvis/Groin", symptoms: ["pelvic pain", "groin pain"] },
  pubic: { label: "Pubic Area", symptoms: ["pubic bone pain", "symphysis pain"] },
  leftGroin: { label: "Left Groin", symptoms: ["left groin pain", "inguinal pain left"] },
  rightGroin: { label: "Right Groin", symptoms: ["right groin pain", "inguinal pain right"] },
  leftHip: { label: "Left Hip (Front)", symptoms: ["left hip pain", "hip arthritis"] },
  rightHip: { label: "Right Hip (Front)", symptoms: ["right hip pain", "hip arthritis"] },
  leftHipSide: { label: "Left Hip (Side)", symptoms: ["left hip lateral pain", "trochanteric pain"] },
  rightHipSide: { label: "Right Hip (Side)", symptoms: ["right hip lateral pain", "trochanteric pain"] },
  
  // ========== BACK ==========
  upperBack: { label: "Upper Back (Center)", symptoms: ["upper back pain", "thoracic pain"] },
  leftUpperBack: { label: "Upper Back (Left)", symptoms: ["left upper back pain"] },
  rightUpperBack: { label: "Upper Back (Right)", symptoms: ["right upper back pain"] },
  leftScapula: { label: "Left Shoulder Blade", symptoms: ["left shoulder blade pain"] },
  rightScapula: { label: "Right Shoulder Blade", symptoms: ["right shoulder blade pain"] },
  spine: { label: "Spine (Middle)", symptoms: ["spine pain", "vertebral pain"] },
  spineUpper: { label: "Spine (Upper/Cervical)", symptoms: ["cervical spine pain"] },
  spineLower: { label: "Spine (Lower/Lumbar)", symptoms: ["lumbar spine pain"] },
  midBack: { label: "Mid Back (Center)", symptoms: ["mid back pain", "back muscle pain"] },
  leftMidBack: { label: "Mid Back (Left)", symptoms: ["left mid back pain"] },
  rightMidBack: { label: "Mid Back (Right)", symptoms: ["right mid back pain"] },
  lowerBack: { label: "Lower Back (Center)", symptoms: ["lower back pain", "lumbar pain", "sciatica"] },
  leftLowerBack: { label: "Lower Back (Left)", symptoms: ["left lower back pain"] },
  rightLowerBack: { label: "Lower Back (Right)", symptoms: ["right lower back pain"] },
  leftKidney: { label: "Left Kidney Area", symptoms: ["left kidney pain", "left flank pain"] },
  rightKidney: { label: "Right Kidney Area", symptoms: ["right kidney pain", "right flank pain"] },
  sacrum: { label: "Sacrum", symptoms: ["sacral pain", "sacroiliac pain"] },
  tailbone: { label: "Tailbone/Coccyx", symptoms: ["tailbone pain", "coccyx pain"] },
  leftGlute: { label: "Left Glute/Buttock", symptoms: ["left buttock pain", "gluteal pain"] },
  rightGlute: { label: "Right Glute/Buttock", symptoms: ["right buttock pain", "gluteal pain"] },
  leftSciatic: { label: "Left Sciatic Nerve", symptoms: ["left sciatica", "nerve pain left leg"] },
  rightSciatic: { label: "Right Sciatic Nerve", symptoms: ["right sciatica", "nerve pain right leg"] },
  
  // ========== LEFT ARM (DETAILED) ==========
  leftBicep: { label: "Left Bicep", symptoms: ["left bicep pain", "upper arm pain"] },
  leftTricep: { label: "Left Tricep", symptoms: ["left tricep pain", "back of arm pain"] },
  leftUpperArmInner: { label: "Left Inner Upper Arm", symptoms: ["left inner arm pain"] },
  leftUpperArmOuter: { label: "Left Outer Upper Arm", symptoms: ["left outer arm pain"] },
  leftElbow: { label: "Left Elbow", symptoms: ["left elbow pain", "tennis elbow"] },
  leftElbowInner: { label: "Left Elbow (Inner)", symptoms: ["left golfer's elbow", "medial epicondyle"] },
  leftElbowOuter: { label: "Left Elbow (Outer)", symptoms: ["left tennis elbow", "lateral epicondyle"] },
  leftForearmTop: { label: "Left Forearm (Top)", symptoms: ["left forearm pain top"] },
  leftForearmBottom: { label: "Left Forearm (Bottom)", symptoms: ["left forearm pain bottom"] },
  leftForearm: { label: "Left Forearm", symptoms: ["left forearm pain"] },
  leftWrist: { label: "Left Wrist", symptoms: ["left wrist pain", "carpal tunnel"] },
  leftWristTop: { label: "Left Wrist (Top)", symptoms: ["left dorsal wrist pain"] },
  leftWristBottom: { label: "Left Wrist (Bottom)", symptoms: ["left palmar wrist pain"] },
  leftPalm: { label: "Left Palm", symptoms: ["left palm pain", "hand cramp"] },
  leftBackHand: { label: "Left Back of Hand", symptoms: ["left hand dorsal pain"] },
  leftThumb: { label: "Left Thumb", symptoms: ["left thumb pain", "de Quervain's"] },
  leftIndexFinger: { label: "Left Index Finger", symptoms: ["left index finger pain"] },
  leftMiddleFinger: { label: "Left Middle Finger", symptoms: ["left middle finger pain"] },
  leftRingFinger: { label: "Left Ring Finger", symptoms: ["left ring finger pain"] },
  leftPinky: { label: "Left Pinky Finger", symptoms: ["left pinky pain", "ulnar nerve"] },
  leftFingers: { label: "Left Fingers (All)", symptoms: ["left finger pain", "finger numbness"] },
  
  // ========== RIGHT ARM (DETAILED) ==========
  rightBicep: { label: "Right Bicep", symptoms: ["right bicep pain", "upper arm pain"] },
  rightTricep: { label: "Right Tricep", symptoms: ["right tricep pain", "back of arm pain"] },
  rightUpperArmInner: { label: "Right Inner Upper Arm", symptoms: ["right inner arm pain"] },
  rightUpperArmOuter: { label: "Right Outer Upper Arm", symptoms: ["right outer arm pain"] },
  rightElbow: { label: "Right Elbow", symptoms: ["right elbow pain", "tennis elbow"] },
  rightElbowInner: { label: "Right Elbow (Inner)", symptoms: ["right golfer's elbow", "medial epicondyle"] },
  rightElbowOuter: { label: "Right Elbow (Outer)", symptoms: ["right tennis elbow", "lateral epicondyle"] },
  rightForearmTop: { label: "Right Forearm (Top)", symptoms: ["right forearm pain top"] },
  rightForearmBottom: { label: "Right Forearm (Bottom)", symptoms: ["right forearm pain bottom"] },
  rightForearm: { label: "Right Forearm", symptoms: ["right forearm pain"] },
  rightWrist: { label: "Right Wrist", symptoms: ["right wrist pain", "carpal tunnel"] },
  rightWristTop: { label: "Right Wrist (Top)", symptoms: ["right dorsal wrist pain"] },
  rightWristBottom: { label: "Right Wrist (Bottom)", symptoms: ["right palmar wrist pain"] },
  rightPalm: { label: "Right Palm", symptoms: ["right palm pain", "hand cramp"] },
  rightBackHand: { label: "Right Back of Hand", symptoms: ["right hand dorsal pain"] },
  rightThumb: { label: "Right Thumb", symptoms: ["right thumb pain", "de Quervain's"] },
  rightIndexFinger: { label: "Right Index Finger", symptoms: ["right index finger pain"] },
  rightMiddleFinger: { label: "Right Middle Finger", symptoms: ["right middle finger pain"] },
  rightRingFinger: { label: "Right Ring Finger", symptoms: ["right ring finger pain"] },
  rightPinky: { label: "Right Pinky Finger", symptoms: ["right pinky pain", "ulnar nerve"] },
  rightFingers: { label: "Right Fingers (All)", symptoms: ["right finger pain", "finger numbness"] },
  
  // ========== LEFT LEG (DETAILED) ==========
  leftQuad: { label: "Left Quadricep", symptoms: ["left quad pain", "front thigh pain"] },
  leftHamstring: { label: "Left Hamstring", symptoms: ["left hamstring pain", "back thigh pain"] },
  leftInnerThigh: { label: "Left Inner Thigh", symptoms: ["left adductor pain", "groin strain"] },
  leftOuterThigh: { label: "Left Outer Thigh", symptoms: ["left IT band pain", "outer thigh pain"] },
  leftThighFront: { label: "Left Front Thigh", symptoms: ["left anterior thigh pain"] },
  leftThighBack: { label: "Left Back Thigh", symptoms: ["left posterior thigh pain"] },
  leftKnee: { label: "Left Knee (Front)", symptoms: ["left knee pain", "kneecap pain"] },
  leftKneeBack: { label: "Left Knee (Back)", symptoms: ["left knee back pain", "baker's cyst"] },
  leftKneeInner: { label: "Left Knee (Inner)", symptoms: ["left medial knee pain"] },
  leftKneeOuter: { label: "Left Knee (Outer)", symptoms: ["left lateral knee pain"] },
  leftShin: { label: "Left Shin", symptoms: ["left shin pain", "shin splints"] },
  leftCalf: { label: "Left Calf", symptoms: ["left calf pain", "calf cramp", "calf strain"] },
  leftAchilles: { label: "Left Achilles Tendon", symptoms: ["left Achilles pain", "tendinitis"] },
  leftAnkle: { label: "Left Ankle (Outer)", symptoms: ["left ankle pain", "ankle sprain"] },
  leftAnkleInner: { label: "Left Ankle (Inner)", symptoms: ["left inner ankle pain", "medial ankle"] },
  leftHeel: { label: "Left Heel", symptoms: ["left heel pain", "plantar fasciitis"] },
  leftArch: { label: "Left Foot Arch", symptoms: ["left arch pain", "flat feet pain"] },
  leftBallFoot: { label: "Left Ball of Foot", symptoms: ["left metatarsal pain", "ball of foot pain"] },
  leftBigToe: { label: "Left Big Toe", symptoms: ["left big toe pain", "gout", "bunion"] },
  leftSmallToes: { label: "Left Small Toes", symptoms: ["left toe pain", "hammer toe"] },
  leftToes: { label: "Left Toes (All)", symptoms: ["left toe pain", "toe numbness"] },
  leftTopFoot: { label: "Left Top of Foot", symptoms: ["left dorsal foot pain"] },
  leftSoleFoot: { label: "Left Sole of Foot", symptoms: ["left plantar pain", "sole pain"] },
  
  // ========== RIGHT LEG (DETAILED) ==========
  rightQuad: { label: "Right Quadricep", symptoms: ["right quad pain", "front thigh pain"] },
  rightHamstring: { label: "Right Hamstring", symptoms: ["right hamstring pain", "back thigh pain"] },
  rightInnerThigh: { label: "Right Inner Thigh", symptoms: ["right adductor pain", "groin strain"] },
  rightOuterThigh: { label: "Right Outer Thigh", symptoms: ["right IT band pain", "outer thigh pain"] },
  rightThighFront: { label: "Right Front Thigh", symptoms: ["right anterior thigh pain"] },
  rightThighBack: { label: "Right Back Thigh", symptoms: ["right posterior thigh pain"] },
  rightKnee: { label: "Right Knee (Front)", symptoms: ["right knee pain", "kneecap pain"] },
  rightKneeBack: { label: "Right Knee (Back)", symptoms: ["right knee back pain", "baker's cyst"] },
  rightKneeInner: { label: "Right Knee (Inner)", symptoms: ["right medial knee pain"] },
  rightKneeOuter: { label: "Right Knee (Outer)", symptoms: ["right lateral knee pain"] },
  rightShin: { label: "Right Shin", symptoms: ["right shin pain", "shin splints"] },
  rightCalf: { label: "Right Calf", symptoms: ["right calf pain", "calf cramp", "calf strain"] },
  rightAchilles: { label: "Right Achilles Tendon", symptoms: ["right Achilles pain", "tendinitis"] },
  rightAnkle: { label: "Right Ankle (Outer)", symptoms: ["right ankle pain", "ankle sprain"] },
  rightAnkleInner: { label: "Right Ankle (Inner)", symptoms: ["right inner ankle pain", "medial ankle"] },
  rightHeel: { label: "Right Heel", symptoms: ["right heel pain", "plantar fasciitis"] },
  rightArch: { label: "Right Foot Arch", symptoms: ["right arch pain", "flat feet pain"] },
  rightBallFoot: { label: "Right Ball of Foot", symptoms: ["right metatarsal pain", "ball of foot pain"] },
  rightBigToe: { label: "Right Big Toe", symptoms: ["right big toe pain", "gout", "bunion"] },
  rightSmallToes: { label: "Right Small Toes", symptoms: ["right toe pain", "hammer toe"] },
  rightToes: { label: "Right Toes (All)", symptoms: ["right toe pain", "toe numbness"] },
  rightTopFoot: { label: "Right Top of Foot", symptoms: ["right dorsal foot pain"] },
  rightSoleFoot: { label: "Right Sole of Foot", symptoms: ["right plantar pain", "sole pain"] },
};

// SVG Human Skeleton Front View - BRIGHT OUTLINED SKELETON
const HumanBodyFront = ({ selectedParts, hoveredPart, onSelect, onHover }) => {
  // Color scheme for different body regions
  const regionColors = {
    head: { fill: 'rgba(147, 112, 219, 0.25)', stroke: '#9370db' },      // Purple - Head
    neck: { fill: 'rgba(255, 165, 0, 0.25)', stroke: '#ffa500' },        // Orange - Neck
    shoulder: { fill: 'rgba(30, 144, 255, 0.25)', stroke: '#1e90ff' },   // Blue - Shoulders
    chest: { fill: 'rgba(255, 105, 180, 0.25)', stroke: '#ff69b4' },     // Pink - Chest
    arm: { fill: 'rgba(0, 206, 209, 0.25)', stroke: '#00ced1' },         // Cyan - Arms
    abdomen: { fill: 'rgba(50, 205, 50, 0.25)', stroke: '#32cd32' },     // Green - Abdomen
    pelvis: { fill: 'rgba(255, 215, 0, 0.25)', stroke: '#ffd700' },      // Gold - Pelvis
    leg: { fill: 'rgba(255, 127, 80, 0.25)', stroke: '#ff7f50' },        // Coral - Legs
    foot: { fill: 'rgba(138, 43, 226, 0.25)', stroke: '#8a2be2' },       // Violet - Feet
  };

  const getRegion = (id) => {
    if (/head|forehead|temple|eye|nose|cheek|ear|mouth|chin|jaw|skull/i.test(id)) return 'head';
    if (/neck|throat/i.test(id)) return 'neck';
    if (/shoulder|deltoid|collarbone|rotator|trapezius|scapula/i.test(id)) return 'shoulder';
    if (/pec|sternum|heart|rib|chest/i.test(id)) return 'chest';
    if (/bicep|tricep|elbow|forearm|wrist|palm|finger|hand/i.test(id)) return 'arm';
    if (/abdomen|liver|spleen|stomach|navel|kidney|back/i.test(id)) return 'abdomen';
    if (/pelvis|hip|groin|glute|sacrum|tailbone/i.test(id)) return 'pelvis';
    if (/quad|thigh|knee|shin|calf|hamstring|achilles/i.test(id)) return 'leg';
    if (/ankle|toe|foot|heel|sole/i.test(id)) return 'foot';
    return 'head';
  };

  const getColor = (id) => {
    if (selectedParts.includes(id)) return 'rgba(255, 60, 60, 0.6)';
    if (hoveredPart === id) return 'rgba(0, 255, 200, 0.5)';
    return regionColors[getRegion(id)]?.fill || 'rgba(255,255,255,0.15)';
  };
  
  const getStroke = (id) => {
    if (selectedParts.includes(id)) return '#ff3333';
    if (hoveredPart === id) return '#00ffcc';
    return regionColors[getRegion(id)]?.stroke || '#ffffff';
  };

  const Part = ({ id, d, cx, cy, rx, ry, x, y, width, height, r, type = 'path' }) => {
    const isActive = selectedParts.includes(id) || hoveredPart === id;
    const props = {
      fill: getColor(id),
      stroke: getStroke(id),
      strokeWidth: isActive ? 3 : 1.8,
      onClick: (e) => { e.stopPropagation(); onSelect(id); },
      onMouseEnter: () => onHover(id),
      onMouseLeave: () => onHover(null),
      style: { cursor: 'pointer', transition: 'all 0.15s ease' }
    };
    
    if (type === 'ellipse') return <ellipse cx={cx} cy={cy} rx={rx} ry={ry} {...props} />;
    if (type === 'rect') return <rect x={x} y={y} width={width} height={height} rx={r || 2} {...props} />;
    if (type === 'circle') return <circle cx={cx} cy={cy} r={r} {...props} />;
    return <path d={d} {...props} />;
  };

  return (
    <svg viewBox="0 0 200 520" className="body-svg" style={{ background: 'transparent' }}>
      
      {/* ===== SKELETON OUTLINE - COLORED BY REGION ===== */}
      <g fill="none" strokeWidth="1.2" strokeLinecap="round">
        
        {/* SKULL - Purple */}
        <g stroke="#9370db">
          <ellipse cx={100} cy={35} rx={28} ry={32} />
          <ellipse cx={88} cy={32} rx={8} ry={6} />
          <ellipse cx={112} cy={32} rx={8} ry={6} />
          <path d="M100 38 L100 50 M95 50 L105 50" />
          <path d="M88 58 Q100 65 112 58" />
          <rect x={90} y={56} width={20} height={8} rx={2} />
        </g>
        
        {/* NECK/SPINE - Orange */}
        <g stroke="#ffa500">
          <line x1={100} y1={67} x2={100} y2={90} strokeWidth="3" />
        </g>
        
        {/* SHOULDERS - Blue */}
        <g stroke="#1e90ff">
          <path d="M100 95 Q80 88 55 100" strokeWidth="2" />
          <path d="M100 95 Q120 88 145 100" strokeWidth="2" />
          <ellipse cx={55} cy={105} rx={12} ry={8} />
          <ellipse cx={145} cy={105} rx={12} ry={8} />
        </g>
        
        {/* RIBCAGE - Pink */}
        <g stroke="#ff69b4">
          <ellipse cx={100} cy={150} rx={38} ry={55} />
          <path d="M62 115 Q100 105 138 115" />
          <path d="M58 130 Q100 118 142 130" />
          <path d="M56 145 Q100 132 144 145" />
          <path d="M58 160 Q100 148 142 160" />
          <path d="M62 175 Q100 165 138 175" />
          <path d="M68 188 Q100 180 132 188" />
          <line x1={100} y1={100} x2={100} y2={195} strokeWidth="2.5" />
        </g>
        
        {/* SPINE - Green */}
        <g stroke="#32cd32">
          <line x1={100} y1={195} x2={100} y2={280} strokeWidth="2.5" />
        </g>
        
        {/* PELVIS - Gold */}
        <g stroke="#ffd700">
          <path d="M62 270 Q55 290 60 315 Q75 340 100 345 Q125 340 140 315 Q145 290 138 270" strokeWidth="2" />
          <ellipse cx={72} cy={310} rx={8} ry={12} />
          <ellipse cx={128} cy={310} rx={8} ry={12} />
        </g>
        
        {/* LEFT ARM - Cyan */}
        <g stroke="#00ced1">
          <line x1={45} y1={110} x2={35} y2={200} strokeWidth="3" />
          <ellipse cx={35} cy={205} rx={6} ry={8} />
          <line x1={32} y1={213} x2={22} y2={300} strokeWidth="2" />
          <line x1={38} y1={213} x2={28} y2={300} strokeWidth="2" />
          <ellipse cx={20} cy={310} rx={12} ry={8} />
          <line x1={12} y1={318} x2={8} y2={345} />
          <line x1={17} y1={318} x2={15} y2={350} />
          <line x1={22} y1={318} x2={22} y2={352} />
          <line x1={27} y1={318} x2={29} y2={350} />
          <line x1={32} y1={318} x2={36} y2={342} />
        </g>
        
        {/* RIGHT ARM - Cyan */}
        <g stroke="#00ced1">
          <line x1={155} y1={110} x2={165} y2={200} strokeWidth="3" />
          <ellipse cx={165} cy={205} rx={6} ry={8} />
          <line x1={162} y1={213} x2={172} y2={300} strokeWidth="2" />
          <line x1={168} y1={213} x2={178} y2={300} strokeWidth="2" />
          <ellipse cx={180} cy={310} rx={12} ry={8} />
          <line x1={172} y1={318} x2={168} y2={342} />
          <line x1={177} y1={318} x2={175} y2={350} />
          <line x1={182} y1={318} x2={182} y2={352} />
          <line x1={187} y1={318} x2={189} y2={350} />
          <line x1={192} y1={318} x2={196} y2={345} />
        </g>
        
        {/* LEFT LEG - Coral */}
        <g stroke="#ff7f50">
          <line x1={72} y1={322} x2={68} y2={420} strokeWidth="4" />
          <ellipse cx={68} cy={428} rx={10} ry={12} />
          <line x1={65} y1={440} x2={62} y2={500} strokeWidth="3" />
          <line x1={71} y1={440} x2={68} y2={500} strokeWidth="2" />
        </g>
        
        {/* RIGHT LEG - Coral */}
        <g stroke="#ff7f50">
          <line x1={128} y1={322} x2={132} y2={420} strokeWidth="4" />
          <ellipse cx={132} cy={428} rx={10} ry={12} />
          <line x1={129} y1={440} x2={132} y2={500} strokeWidth="3" />
          <line x1={135} y1={440} x2={138} y2={500} strokeWidth="2" />
        </g>
        
        {/* FEET - Violet */}
        <g stroke="#8a2be2">
          <ellipse cx={60} cy={508} rx={16} ry={6} />
          <ellipse cx={140} cy={508} rx={16} ry={6} />
        </g>
      </g>
      
      {/* ===== CLICKABLE REGIONS ===== */}
      {/* HEAD */}
      <Part id="head" type="ellipse" cx={100} cy={20} rx={20} ry={14} />
      <Part id="forehead" type="path" d="M80 8 Q100 0 120 8 L118 24 Q100 16 82 24 Z" />
      <Part id="leftTemple" type="ellipse" cx={76} cy={28} rx={6} ry={10} />
      <Part id="rightTemple" type="ellipse" cx={124} cy={28} rx={6} ry={10} />
      <Part id="leftEye" type="ellipse" cx={88} cy={32} rx={8} ry={6} />
      <Part id="rightEye" type="ellipse" cx={112} cy={32} rx={8} ry={6} />
      <Part id="nose" type="path" d="M95 38 L100 52 L105 38 Z" />
      <Part id="leftCheek" type="ellipse" cx={82} cy={48} rx={6} ry={6} />
      <Part id="rightCheek" type="ellipse" cx={118} cy={48} rx={6} ry={6} />
      <Part id="leftEar" type="ellipse" cx={70} cy={38} rx={4} ry={8} />
      <Part id="rightEar" type="ellipse" cx={130} cy={38} rx={4} ry={8} />
      <Part id="mouth" type="ellipse" cx={100} cy={58} rx={10} ry={4} />
      <Part id="chin" type="ellipse" cx={100} cy={66} rx={8} ry={5} />
      <Part id="jaw" type="path" d="M80 50 Q100 72 120 50 L116 44 Q100 62 84 44 Z" />
      
      {/* NECK */}
      <Part id="neckLeft" type="rect" x={88} y={68} width={8} height={20} />
      <Part id="neck" type="rect" x={94} y={68} width={12} height={20} />
      <Part id="neckRight" type="rect" x={104} y={68} width={8} height={20} />
      <Part id="throat" type="ellipse" cx={100} cy={80} rx={8} ry={6} />
      
      {/* SHOULDERS */}
      <Part id="leftShoulder" type="ellipse" cx={55} cy={105} rx={14} ry={10} />
      <Part id="rightShoulder" type="ellipse" cx={145} cy={105} rx={14} ry={10} />
      <Part id="leftDeltoid" type="path" d="M42 100 Q52 92 68 105 L62 125 Q48 118 40 108 Z" />
      <Part id="rightDeltoid" type="path" d="M158 100 Q148 92 132 105 L138 125 Q152 118 160 108 Z" />
      <Part id="leftCollarbone" type="path" d="M65 92 Q82 88 100 95 L98 102 Q80 96 65 102 Z" />
      <Part id="rightCollarbone" type="path" d="M135 92 Q118 88 100 95 L102 102 Q120 96 135 102 Z" />
      
      {/* CHEST */}
      <Part id="leftPec" type="path" d="M62 108 Q80 102 98 118 L95 145 Q75 138 62 125 Z" />
      <Part id="rightPec" type="path" d="M138 108 Q120 102 102 118 L105 145 Q125 138 138 125 Z" />
      <Part id="sternum" type="rect" x={95} y={105} width={10} height={40} />
      <Part id="heart" type="ellipse" cx={88} cy={130} rx={10} ry={12} />
      <Part id="leftRibs" type="path" d="M62 130 L65 158 Q80 168 95 160 L92 130 Z" />
      <Part id="rightRibs" type="path" d="M138 130 L135 158 Q120 168 105 160 L108 130 Z" />
      
      {/* ARMS */}
      <Part id="leftBicep" type="path" d="M38 118 Q32 150 30 185 L44 188 Q45 155 48 122 Z" />
      <Part id="leftElbow" type="ellipse" cx={35} cy={205} rx={10} ry={12} />
      <Part id="leftForearm" type="path" d="M26 218 Q20 255 18 295 L32 298 Q35 260 38 222 Z" />
      <Part id="leftWrist" type="ellipse" cx={22} cy={305} rx={8} ry={6} />
      <Part id="leftPalm" type="ellipse" cx={18} cy={325} rx={10} ry={14} />
      <Part id="leftFingers" type="path" d="M6 340 L2 375 L34 375 L30 340 Z" />
      
      <Part id="rightBicep" type="path" d="M162 118 Q168 150 170 185 L156 188 Q155 155 152 122 Z" />
      <Part id="rightElbow" type="ellipse" cx={165} cy={205} rx={10} ry={12} />
      <Part id="rightForearm" type="path" d="M174 218 Q180 255 182 295 L168 298 Q165 260 162 222 Z" />
      <Part id="rightWrist" type="ellipse" cx={178} cy={305} rx={8} ry={6} />
      <Part id="rightPalm" type="ellipse" cx={182} cy={325} rx={10} ry={14} />
      <Part id="rightFingers" type="path" d="M194 340 L198 375 L166 375 L170 340 Z" />
      
      {/* ABDOMEN */}
      <Part id="upperAbdomen" type="rect" x={78} y={150} width={44} height={25} r={3} />
      <Part id="liver" type="path" d="M108 155 Q132 160 136 178 L130 195 Q115 188 108 175 Z" />
      <Part id="spleen" type="ellipse" cx={72} cy={180} rx={10} ry={14} />
      <Part id="stomach" type="ellipse" cx={100} cy={185} rx={16} ry={14} />
      <Part id="navel" type="circle" cx={100} cy={215} r={6} />
      <Part id="leftAbdomen" type="rect" x={65} y={175} width={18} height={50} r={3} />
      <Part id="rightAbdomen" type="rect" x={117} y={175} width={18} height={50} r={3} />
      <Part id="lowerAbdomen" type="path" d="M70 230 Q100 245 130 230 L126 268 Q100 285 74 268 Z" />
      
      {/* PELVIS */}
      <Part id="pelvis" type="path" d="M65 270 Q100 290 135 270 L130 310 Q100 330 70 310 Z" />
      <Part id="leftHip" type="ellipse" cx={72} cy={310} rx={12} ry={14} />
      <Part id="rightHip" type="ellipse" cx={128} cy={310} rx={12} ry={14} />
      <Part id="leftGroin" type="ellipse" cx={82} cy={332} rx={8} ry={6} />
      <Part id="rightGroin" type="ellipse" cx={118} cy={332} rx={8} ry={6} />
      
      {/* THIGHS */}
      <Part id="leftQuad" type="path" d="M62 340 Q74 350 86 340 L82 410 Q70 420 62 410 Z" />
      <Part id="leftInnerThigh" type="path" d="M86 342 Q94 360 96 385 L90 408 Q82 405 78 400 Z" />
      <Part id="leftOuterThigh" type="path" d="M60 345 L54 405 L62 415 L68 350 Z" />
      
      <Part id="rightQuad" type="path" d="M138 340 Q126 350 114 340 L118 410 Q130 420 138 410 Z" />
      <Part id="rightInnerThigh" type="path" d="M114 342 Q106 360 104 385 L110 408 Q118 405 122 400 Z" />
      <Part id="rightOuterThigh" type="path" d="M140 345 L146 405 L138 415 L132 350 Z" />
      
      {/* KNEES */}
      <Part id="leftKnee" type="ellipse" cx={68} cy={428} rx={14} ry={18} />
      <Part id="rightKnee" type="ellipse" cx={132} cy={428} rx={14} ry={18} />
      
      {/* LOWER LEGS */}
      <Part id="leftShin" type="path" d="M56 448 Q68 458 80 448 L76 495 Q66 505 58 495 Z" />
      <Part id="rightShin" type="path" d="M144 448 Q132 458 120 448 L124 495 Q134 505 142 495 Z" />
      
      {/* FEET */}
      <Part id="leftAnkle" type="ellipse" cx={65} cy={502} rx={10} ry={8} />
      <Part id="rightAnkle" type="ellipse" cx={135} cy={502} rx={10} ry={8} />
      <Part id="leftToes" type="path" d="M42 510 L38 520 L82 520 L78 510 Z" />
      <Part id="rightToes" type="path" d="M158 510 L162 520 L118 520 L122 510 Z" />
    </svg>
  );
};

// SVG Human Skeleton Back View - BRIGHT OUTLINED SKELETON
const HumanBodyBack = ({ selectedParts, hoveredPart, onSelect, onHover }) => {
  // Color scheme for different body regions
  const regionColors = {
    head: { fill: 'rgba(147, 112, 219, 0.25)', stroke: '#9370db' },      // Purple - Head
    neck: { fill: 'rgba(255, 165, 0, 0.25)', stroke: '#ffa500' },        // Orange - Neck
    shoulder: { fill: 'rgba(30, 144, 255, 0.25)', stroke: '#1e90ff' },   // Blue - Shoulders
    chest: { fill: 'rgba(255, 105, 180, 0.25)', stroke: '#ff69b4' },     // Pink - Chest/Back
    arm: { fill: 'rgba(0, 206, 209, 0.25)', stroke: '#00ced1' },         // Cyan - Arms
    abdomen: { fill: 'rgba(50, 205, 50, 0.25)', stroke: '#32cd32' },     // Green - Abdomen
    pelvis: { fill: 'rgba(255, 215, 0, 0.25)', stroke: '#ffd700' },      // Gold - Pelvis
    leg: { fill: 'rgba(255, 127, 80, 0.25)', stroke: '#ff7f50' },        // Coral - Legs
    foot: { fill: 'rgba(138, 43, 226, 0.25)', stroke: '#8a2be2' },       // Violet - Feet
  };

  const getRegion = (id) => {
    if (/head|forehead|temple|eye|nose|cheek|ear|mouth|chin|jaw|skull/i.test(id)) return 'head';
    if (/neck|throat/i.test(id)) return 'neck';
    if (/shoulder|deltoid|collarbone|rotator|trapezius|scapula/i.test(id)) return 'shoulder';
    if (/pec|sternum|heart|rib|chest|back|spine/i.test(id)) return 'chest';
    if (/bicep|tricep|elbow|forearm|wrist|palm|finger|hand/i.test(id)) return 'arm';
    if (/abdomen|liver|spleen|stomach|navel|kidney/i.test(id)) return 'abdomen';
    if (/pelvis|hip|groin|glute|sacrum|tailbone/i.test(id)) return 'pelvis';
    if (/quad|thigh|knee|shin|calf|hamstring|achilles/i.test(id)) return 'leg';
    if (/ankle|toe|foot|heel|sole/i.test(id)) return 'foot';
    return 'head';
  };

  const getColor = (id) => {
    if (selectedParts.includes(id)) return 'rgba(255, 60, 60, 0.6)';
    if (hoveredPart === id) return 'rgba(0, 255, 200, 0.5)';
    return regionColors[getRegion(id)]?.fill || 'rgba(255,255,255,0.15)';
  };
  
  const getStroke = (id) => {
    if (selectedParts.includes(id)) return '#ff3333';
    if (hoveredPart === id) return '#00ffcc';
    return regionColors[getRegion(id)]?.stroke || '#ffffff';
  };

  const Part = ({ id, d, cx, cy, rx, ry, x, y, width, height, r, type = 'path' }) => {
    const isActive = selectedParts.includes(id) || hoveredPart === id;
    const props = {
      fill: getColor(id),
      stroke: getStroke(id),
      strokeWidth: isActive ? 3 : 1.8,
      onClick: (e) => { e.stopPropagation(); onSelect(id); },
      onMouseEnter: () => onHover(id),
      onMouseLeave: () => onHover(null),
      style: { cursor: 'pointer', transition: 'all 0.15s ease' }
    };
    
    if (type === 'ellipse') return <ellipse cx={cx} cy={cy} rx={rx} ry={ry} {...props} />;
    if (type === 'rect') return <rect x={x} y={y} width={width} height={height} rx={r || 2} {...props} />;
    if (type === 'circle') return <circle cx={cx} cy={cy} r={r} {...props} />;
    return <path d={d} {...props} />;
  };

  return (
    <svg viewBox="0 0 200 520" className="body-svg" style={{ background: 'transparent' }}>
      
      {/* ===== SKELETON OUTLINE - COLORED BY REGION (BACK VIEW) ===== */}
      <g fill="none" strokeWidth="1.2" strokeLinecap="round">
        
        {/* SKULL BACK - Purple */}
        <g stroke="#9370db">
          <ellipse cx={100} cy={35} rx={28} ry={32} />
        </g>
        
        {/* SPINE/NECK - Orange */}
        <g stroke="#ffa500">
          <line x1={100} y1={67} x2={100} y2={90} strokeWidth="3" />
          <line x1={100} y1={90} x2={100} y2={280} strokeWidth="3" />
          {/* Vertebrae markers */}
          <line x1={95} y1={100} x2={105} y2={100} strokeWidth="1" />
          <line x1={95} y1={115} x2={105} y2={115} strokeWidth="1" />
          <line x1={95} y1={130} x2={105} y2={130} strokeWidth="1" />
          <line x1={95} y1={145} x2={105} y2={145} strokeWidth="1" />
          <line x1={95} y1={160} x2={105} y2={160} strokeWidth="1" />
          <line x1={95} y1={175} x2={105} y2={175} strokeWidth="1" />
          <line x1={95} y1={190} x2={105} y2={190} strokeWidth="1" />
          <line x1={95} y1={205} x2={105} y2={205} strokeWidth="1" />
          <line x1={95} y1={220} x2={105} y2={220} strokeWidth="1" />
          <line x1={95} y1={235} x2={105} y2={235} strokeWidth="1" />
          <line x1={95} y1={250} x2={105} y2={250} strokeWidth="1" />
          <line x1={95} y1={265} x2={105} y2={265} strokeWidth="1" />
        </g>
        
        {/* SCAPULAE & SHOULDERS - Blue */}
        <g stroke="#1e90ff">
          <path d="M65 105 Q75 95 90 100 L85 145 Q70 140 60 125 Z" strokeWidth="1.5" />
          <path d="M135 105 Q125 95 110 100 L115 145 Q130 140 140 125 Z" strokeWidth="1.5" />
          <path d="M100 95 Q80 88 55 100" strokeWidth="2" />
          <path d="M100 95 Q120 88 145 100" strokeWidth="2" />
        </g>
        
        {/* RIBCAGE BACK - Pink */}
        <g stroke="#ff69b4">
          <ellipse cx={100} cy={150} rx={38} ry={55} />
          <path d="M62 120 Q100 110 138 120" />
          <path d="M58 135 Q100 125 142 135" />
          <path d="M56 150 Q100 140 144 150" />
          <path d="M58 165 Q100 155 142 165" />
          <path d="M62 180 Q100 172 138 180" />
          <path d="M68 192 Q100 185 132 192" />
        </g>
        
        {/* PELVIS BACK - Gold */}
        <g stroke="#ffd700">
          <path d="M62 270 Q55 290 60 315 Q75 340 100 345 Q125 340 140 315 Q145 290 138 270" strokeWidth="2" />
          <ellipse cx={72} cy={310} rx={8} ry={12} />
          <ellipse cx={128} cy={310} rx={8} ry={12} />
          <path d="M92 275 L100 290 L108 275" strokeWidth="1.5" />
        </g>
        
        {/* LEFT ARM BACK - Cyan */}
        <g stroke="#00ced1">
          <line x1={45} y1={110} x2={35} y2={200} strokeWidth="3" />
          <ellipse cx={35} cy={205} rx={6} ry={8} />
          <line x1={32} y1={213} x2={22} y2={300} strokeWidth="2" />
          <line x1={38} y1={213} x2={28} y2={300} strokeWidth="2" />
          <ellipse cx={20} cy={310} rx={12} ry={8} />
          <line x1={12} y1={318} x2={8} y2={345} />
          <line x1={17} y1={318} x2={15} y2={350} />
          <line x1={22} y1={318} x2={22} y2={352} />
          <line x1={27} y1={318} x2={29} y2={350} />
          <line x1={32} y1={318} x2={36} y2={342} />
        </g>
        
        {/* RIGHT ARM BACK - Cyan */}
        <g stroke="#00ced1">
          <line x1={155} y1={110} x2={165} y2={200} strokeWidth="3" />
          <ellipse cx={165} cy={205} rx={6} ry={8} />
          <line x1={162} y1={213} x2={172} y2={300} strokeWidth="2" />
          <line x1={168} y1={213} x2={178} y2={300} strokeWidth="2" />
          <ellipse cx={180} cy={310} rx={12} ry={8} />
          <line x1={172} y1={318} x2={168} y2={342} />
          <line x1={177} y1={318} x2={175} y2={350} />
          <line x1={182} y1={318} x2={182} y2={352} />
          <line x1={187} y1={318} x2={189} y2={350} />
          <line x1={192} y1={318} x2={196} y2={345} />
        </g>
        
        {/* LEFT LEG BACK - Coral */}
        <g stroke="#ff7f50">
          <line x1={72} y1={322} x2={68} y2={420} strokeWidth="4" />
          <ellipse cx={68} cy={428} rx={10} ry={12} />
          <line x1={65} y1={440} x2={62} y2={500} strokeWidth="3" />
          <line x1={71} y1={440} x2={68} y2={500} strokeWidth="2" />
        </g>
        
        {/* RIGHT LEG BACK - Coral */}
        <g stroke="#ff7f50">
          <line x1={128} y1={322} x2={132} y2={420} strokeWidth="4" />
          <ellipse cx={132} cy={428} rx={10} ry={12} />
          <line x1={129} y1={440} x2={132} y2={500} strokeWidth="3" />
          <line x1={135} y1={440} x2={138} y2={500} strokeWidth="2" />
        </g>
        
        {/* FEET - Violet */}
        <g stroke="#8a2be2">
          <ellipse cx={60} cy={508} rx={16} ry={6} />
          <ellipse cx={140} cy={508} rx={16} ry={6} />
        </g>
      </g>
      
      {/* ===== CLICKABLE REGIONS ===== */}
      {/* HEAD BACK */}
      <Part id="head" type="ellipse" cx={100} cy={20} rx={20} ry={14} />
      <Part id="skullBack" type="path" d="M80 8 Q100 0 120 8 L118 35 Q100 22 82 35 Z" />
      
      {/* NECK BACK */}
      <Part id="neckBack" type="rect" x={88} y={68} width={24} height={20} />
      <Part id="neckLeft" type="rect" x={80} y={70} width={10} height={16} />
      <Part id="neckRight" type="rect" x={110} y={70} width={10} height={16} />
      
      {/* TRAPEZIUS & SHOULDERS */}
      <Part id="leftTrapezius" type="path" d="M68 88 Q88 80 100 92 L96 115 Q80 108 66 98 Z" />
      <Part id="rightTrapezius" type="path" d="M132 88 Q112 80 100 92 L104 115 Q120 108 134 98 Z" />
      <Part id="leftShoulder" type="ellipse" cx={55} cy={105} rx={14} ry={10} />
      <Part id="rightShoulder" type="ellipse" cx={145} cy={105} rx={14} ry={10} />
      <Part id="leftRotatorCuff" type="ellipse" cx={58} cy={112} rx={8} ry={6} />
      <Part id="rightRotatorCuff" type="ellipse" cx={142} cy={112} rx={8} ry={6} />
      
      {/* UPPER BACK */}
      <Part id="leftScapula" type="path" d="M60 105 Q78 95 92 105 L88 150 Q70 142 56 128 Z" />
      <Part id="rightScapula" type="path" d="M140 105 Q122 95 108 105 L112 150 Q130 142 144 128 Z" />
      <Part id="upperBack" type="rect" x={88} y={100} width={24} height={40} r={3} />
      <Part id="spine" type="rect" x={96} y={70} width={8} height={200} r={2} />
      
      {/* MID BACK */}
      <Part id="midBack" type="path" d="M62 145 Q100 160 138 145 L135 195 Q100 210 65 195 Z" />
      <Part id="leftMidBack" type="rect" x={62} y={145} width={22} height={48} r={3} />
      <Part id="rightMidBack" type="rect" x={116} y={145} width={22} height={48} r={3} />
      
      {/* LOWER BACK */}
      <Part id="lowerBack" type="path" d="M68 198 Q100 215 132 198 L128 260 Q100 278 72 260 Z" />
      <Part id="leftLowerBack" type="rect" x={68} y={198} width={20} height={55} r={3} />
      <Part id="rightLowerBack" type="rect" x={112} y={198} width={20} height={55} r={3} />
      <Part id="leftKidney" type="ellipse" cx={78} cy={215} rx={12} ry={15} />
      <Part id="rightKidney" type="ellipse" cx={122} cy={215} rx={12} ry={15} />
      <Part id="sacrum" type="ellipse" cx={100} cy={275} rx={12} ry={10} />
      <Part id="tailbone" type="ellipse" cx={100} cy={292} rx={6} ry={8} />
      
      {/* LEFT ARM BACK */}
      <Part id="leftDeltoid" type="path" d="M42 100 Q52 92 68 105 L62 128 Q48 120 40 108 Z" />
      <Part id="leftTricep" type="path" d="M38 118 Q32 150 30 185 L44 188 Q45 155 48 122 Z" />
      <Part id="leftElbow" type="ellipse" cx={35} cy={205} rx={10} ry={12} />
      <Part id="leftForearm" type="path" d="M26 218 Q20 255 18 295 L32 298 Q35 260 38 222 Z" />
      <Part id="leftWrist" type="ellipse" cx={22} cy={305} rx={8} ry={6} />
      <Part id="leftBackHand" type="ellipse" cx={18} cy={325} rx={10} ry={14} />
      <Part id="leftFingers" type="path" d="M6 340 L2 375 L34 375 L30 340 Z" />
      
      {/* RIGHT ARM BACK */}
      <Part id="rightDeltoid" type="path" d="M158 100 Q148 92 132 105 L138 128 Q152 120 160 108 Z" />
      <Part id="rightTricep" type="path" d="M162 118 Q168 150 170 185 L156 188 Q155 155 152 122 Z" />
      <Part id="rightElbow" type="ellipse" cx={165} cy={205} rx={10} ry={12} />
      <Part id="rightForearm" type="path" d="M174 218 Q180 255 182 295 L168 298 Q165 260 162 222 Z" />
      <Part id="rightWrist" type="ellipse" cx={178} cy={305} rx={8} ry={6} />
      <Part id="rightBackHand" type="ellipse" cx={182} cy={325} rx={10} ry={14} />
      <Part id="rightFingers" type="path" d="M194 340 L198 375 L166 375 L170 340 Z" />
      
      {/* GLUTES */}
      <Part id="leftGlute" type="ellipse" cx={80} cy={315} rx={18} ry={20} />
      <Part id="rightGlute" type="ellipse" cx={120} cy={315} rx={18} ry={20} />
      <Part id="leftHipSide" type="ellipse" cx={60} cy={318} rx={8} ry={14} />
      <Part id="rightHipSide" type="ellipse" cx={140} cy={318} rx={8} ry={14} />
      
      {/* HAMSTRINGS */}
      <Part id="leftHamstring" type="path" d="M62 340 Q78 352 90 340 L86 410 Q72 422 64 410 Z" />
      <Part id="rightHamstring" type="path" d="M138 340 Q122 352 110 340 L114 410 Q128 422 136 410 Z" />
      <Part id="leftThighBack" type="rect" x={64} y={345} width={24} height={60} r={4} />
      <Part id="rightThighBack" type="rect" x={112} y={345} width={24} height={60} r={4} />
      
      {/* KNEES BACK */}
      <Part id="leftKneeBack" type="ellipse" cx={68} cy={428} rx={14} ry={18} />
      <Part id="rightKneeBack" type="ellipse" cx={132} cy={428} rx={14} ry={18} />
      
      {/* CALVES */}
      <Part id="leftCalf" type="path" d="M56 448 Q70 462 84 448 L80 495 Q68 508 58 495 Z" />
      <Part id="rightCalf" type="path" d="M144 448 Q130 462 116 448 L120 495 Q132 508 142 495 Z" />
      <Part id="leftAchilles" type="rect" x={62} y={488} width={12} height={20} />
      <Part id="rightAchilles" type="rect" x={126} y={488} width={12} height={20} />
      
      {/* HEELS */}
      <Part id="leftHeel" type="ellipse" cx={65} cy={510} rx={14} ry={8} />
      <Part id="rightHeel" type="ellipse" cx={135} cy={510} rx={14} ry={8} />
    </svg>
  );
};

// Body Icon component
export const BodyIcon = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="4" r="2" />
    <path d="M12 6v2" />
    <path d="M8 8h8l1 8H7l1-8z" />
    <path d="M6.5 10l-2 6" />
    <path d="M17.5 10l2 6" />
    <path d="M9 16l-1 7" />
    <path d="M15 16l1 7" />
  </svg>
);

// Main Component
export default function BodySelector({ onSelectSymptoms, onClose, language = 'en' }) {
  const [selectedParts, setSelectedParts] = useState([]);
  const [hoveredPart, setHoveredPart] = useState(null);

  const translations = {
    en: {
      title: "Where does it hurt?",
      subtitle: "Click on all the areas where you feel pain or discomfort",
      front: "FRONT",
      back: "BACK",
      selected: "Selected areas:",
      confirm: "Confirm Selection",
      clear: "Clear All",
      cancel: "Cancel",
      parts: "body parts"
    },
    ta: {
      title: "எங்கே வலிக்கிறது?",
      subtitle: "வலி உணரும் அனைத்து இடங்களையும் கிளிக் செய்யவும்",
      front: "முன்",
      back: "பின்",
      selected: "தேர்வு செய்தவை:",
      confirm: "உறுதிப்படுத்து",
      clear: "அழி",
      cancel: "ரத்து",
      parts: "உடல் பாகங்கள்"
    },
    hi: {
      title: "दर्द कहाँ है?",
      subtitle: "जहाँ भी दर्द या परेशानी है वहाँ क्लिक करें",
      front: "सामने",
      back: "पीछे",
      selected: "चुने गए क्षेत्र:",
      confirm: "पुष्टि करें",
      clear: "साफ़ करें",
      cancel: "रद्द करें",
      parts: "शरीर के अंग"
    }
  };

  const t = translations[language] || translations.en;

  const handleSelect = (id) => {
    setSelectedParts(prev => 
      prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]
    );
  };

  const handleConfirm = () => {
    const symptoms = selectedParts
      .map(p => BODY_REGIONS[p]?.symptoms[0])
      .filter(Boolean);
    const labels = selectedParts
      .map(p => BODY_REGIONS[p]?.label)
      .filter(Boolean);
    
    if (symptoms.length > 0) {
      onSelectSymptoms(symptoms, labels);
    }
    onClose();
  };

  return (
    <div className="body-selector-overlay">
      <div className="body-selector-modal body-selector-large">
        {/* Header */}
        <div className="body-selector-header">
          <div className="body-selector-title">
            <BodyIcon size={26} color="#ff6b6b" />
            <h2>{t.title}</h2>
          </div>
          <p>{t.subtitle}</p>
          <small>🎯 {Object.keys(BODY_REGIONS).length} {t.parts}</small>
        </div>

        {/* Body SVG Container */}
        <div className="body-svg-container">
          {/* Front View */}
          <div className="body-view">
            <div className="view-label">{t.front}</div>
            <HumanBodyFront
              selectedParts={selectedParts}
              hoveredPart={hoveredPart}
              onSelect={handleSelect}
              onHover={setHoveredPart}
            />
          </div>
          
          {/* Back View */}
          <div className="body-view">
            <div className="view-label">{t.back}</div>
            <HumanBodyBack
              selectedParts={selectedParts}
              hoveredPart={hoveredPart}
              onSelect={handleSelect}
              onHover={setHoveredPart}
            />
          </div>
          
          {/* Hover Tooltip */}
          {hoveredPart && (
            <div className="body-hover-tooltip">
              📍 {BODY_REGIONS[hoveredPart]?.label}
            </div>
          )}
        </div>

        {/* Selected Parts */}
        {selectedParts.length > 0 && (
          <div className="body-selector-selected">
            <strong>{t.selected}</strong>
            <div className="selected-parts-list">
              {selectedParts.map(id => (
                <span key={id} className="selected-part-tag">
                  {BODY_REGIONS[id]?.label}
                  <button onClick={() => handleSelect(id)}>×</button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="body-selector-actions">
          <button className="btn-cancel" onClick={onClose}>
            {t.cancel}
          </button>
          <button className="btn-clear" onClick={() => setSelectedParts([])}>
            {t.clear}
          </button>
          <button 
            className="btn-confirm" 
            onClick={handleConfirm}
            disabled={selectedParts.length === 0}
          >
            {t.confirm} ({selectedParts.length})
          </button>
        </div>
      </div>
    </div>
  );
}

import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

// DNA Helix Particle System
function DNAHelix() {
  const points = useRef()
  const particleCount = 200
  
  const { positions, colors } = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    const colors = new Float32Array(particleCount * 3)
    
    for (let i = 0; i < particleCount; i++) {
      const t = (i / particleCount) * Math.PI * 8
      const radius = 2
      
      // DNA double helix pattern
      const strand = i % 2
      const x = Math.cos(t + strand * Math.PI) * radius
      const y = (i / particleCount) * 10 - 5
      const z = Math.sin(t + strand * Math.PI) * radius
      
      positions[i * 3] = x
      positions[i * 3 + 1] = y
      positions[i * 3 + 2] = z
      
      // Gradient colors - teal to purple
      const colorMix = i / particleCount
      colors[i * 3] = 0.0 + colorMix * 0.4     // R
      colors[i * 3 + 1] = 0.83 - colorMix * 0.5 // G
      colors[i * 3 + 2] = 0.67 + colorMix * 0.3 // B
    }
    
    return { positions, colors }
  }, [])
  
  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y = state.clock.elapsedTime * 0.1
      points.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.05) * 0.1
    }
  })
  
  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.15}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  )
}

// Floating Medical Particles
function FloatingParticles() {
  const mesh = useRef()
  const particleCount = 100
  
  const particles = useMemo(() => {
    const positions = new Float32Array(particleCount * 3)
    
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10
    }
    
    return positions
  }, [])
  
  useFrame((state) => {
    if (mesh.current) {
      const positions = mesh.current.geometry.attributes.position.array
      
      for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3
        positions[i3 + 1] += Math.sin(state.clock.elapsedTime + i) * 0.002
        positions[i3] += Math.cos(state.clock.elapsedTime * 0.5 + i) * 0.001
      }
      
      mesh.current.geometry.attributes.position.needsUpdate = true
    }
  })
  
  return (
    <points ref={mesh}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        color="#00D4AA"
        transparent
        opacity={0.4}
        sizeAttenuation
      />
    </points>
  )
}

// Gradient Mesh Background
function GradientSphere() {
  const mesh = useRef()
  
  useFrame((state) => {
    if (mesh.current) {
      mesh.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1
      mesh.current.rotation.y = state.clock.elapsedTime * 0.05
      mesh.current.scale.x = 1 + Math.sin(state.clock.elapsedTime * 0.3) * 0.05
      mesh.current.scale.y = 1 + Math.cos(state.clock.elapsedTime * 0.3) * 0.05
    }
  })
  
  return (
    <mesh ref={mesh} position={[0, 0, -5]}>
      <sphereGeometry args={[8, 64, 64]} />
      <meshBasicMaterial
        color="#667eea"
        transparent
        opacity={0.1}
        wireframe
      />
    </mesh>
  )
}

// Pulse Ring Effect
function PulseRings() {
  const ring1 = useRef()
  const ring2 = useRef()
  const ring3 = useRef()
  
  useFrame((state) => {
    const t = state.clock.elapsedTime
    
    if (ring1.current) {
      ring1.current.scale.setScalar(1 + Math.sin(t * 0.5) * 0.3)
      ring1.current.material.opacity = 0.3 - Math.sin(t * 0.5) * 0.2
    }
    if (ring2.current) {
      ring2.current.scale.setScalar(1 + Math.sin(t * 0.5 + 1) * 0.3)
      ring2.current.material.opacity = 0.3 - Math.sin(t * 0.5 + 1) * 0.2
    }
    if (ring3.current) {
      ring3.current.scale.setScalar(1 + Math.sin(t * 0.5 + 2) * 0.3)
      ring3.current.material.opacity = 0.3 - Math.sin(t * 0.5 + 2) * 0.2
    }
  })
  
  return (
    <group position={[0, 0, -3]}>
      <mesh ref={ring1}>
        <ringGeometry args={[2, 2.1, 64]} />
        <meshBasicMaterial color="#00D4AA" transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>
      <mesh ref={ring2}>
        <ringGeometry args={[2.5, 2.6, 64]} />
        <meshBasicMaterial color="#667eea" transparent opacity={0.2} side={THREE.DoubleSide} />
      </mesh>
      <mesh ref={ring3}>
        <ringGeometry args={[3, 3.1, 64]} />
        <meshBasicMaterial color="#764ba2" transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>
    </group>
  )
}

// Heart Beat Line
function HeartbeatLine() {
  const line = useRef()
  const pointCount = 100
  
  const positions = useMemo(() => {
    return new Float32Array(pointCount * 3)
  }, [])
  
  useFrame((state) => {
    if (line.current) {
      const t = state.clock.elapsedTime
      
      for (let i = 0; i < pointCount; i++) {
        const x = (i / pointCount) * 16 - 8
        const offset = (i / pointCount + t * 0.3) % 1
        
        // ECG-like pattern
        let y = 0
        const phase = offset * Math.PI * 2
        
        if (phase > 2.5 && phase < 2.7) {
          y = Math.sin((phase - 2.5) * 15) * 1.5
        } else if (phase > 2.7 && phase < 3.2) {
          y = -Math.sin((phase - 2.7) * 6) * 0.5
        } else if (phase > 3.4 && phase < 3.6) {
          y = Math.sin((phase - 3.4) * 15) * 0.8
        }
        
        positions[i * 3] = x
        positions[i * 3 + 1] = y - 3
        positions[i * 3 + 2] = 0
      }
      
      line.current.geometry.attributes.position.needsUpdate = true
    }
  })
  
  return (
    <line ref={line}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={pointCount}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial color="#00D4AA" transparent opacity={0.3} />
    </line>
  )
}

// Main WebGL Background Component
export default function WebGLBackground({ contained = false }) {
  return (
    <div
      style={{
        position: contained ? 'absolute' : 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
        background: contained ? 'transparent' : 'linear-gradient(135deg, #0A2540 0%, #1a365d 50%, #2d3748 100%)',
      }}
    >
      <Canvas
        camera={{ position: [0, 0, 10], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.5} />
        <DNAHelix />
        <FloatingParticles />
        <GradientSphere />
        <PulseRings />
        <HeartbeatLine />
      </Canvas>
      
      {/* Gradient Overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: `
            radial-gradient(ellipse at 20% 20%, rgba(0, 212, 170, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(118, 75, 162, 0.1) 0%, transparent 70%)
          `,
          pointerEvents: 'none',
        }}
      />
    </div>
  )
}

// Lighter version for better performance on mobile
export function WebGLBackgroundLite() {
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
        background: 'linear-gradient(135deg, #0A2540 0%, #1a365d 50%, #2d3748 100%)',
      }}
    >
      <Canvas
        camera={{ position: [0, 0, 10], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.5} />
        <FloatingParticles />
        <PulseRings />
      </Canvas>
      
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: `
            radial-gradient(ellipse at 20% 20%, rgba(0, 212, 170, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(102, 126, 234, 0.15) 0%, transparent 50%)
          `,
          pointerEvents: 'none',
        }}
      />
    </div>
  )
}

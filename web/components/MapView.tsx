'use client'

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Creator } from '@/types'

// Fix Leaflet default icon issue with webpack/Next.js
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

// City coordinates for marker placement.
// Toronto is the primary market — listed first.
// Other coords are kept so legacy creator pins still resolve.
const CITY_COORDS: Record<string, [number, number]> = {
  // ── Primary market ──
  'Toronto': [43.6532, -79.3832],
  // ── Other Canadian cities ──
  'Vancouver': [49.2827, -123.1207],
  'Montreal': [45.5019, -73.5674],
  'Calgary': [51.0447, -114.0719],
  'Ottawa': [45.4215, -75.6972],
  // ── International markets ──
  'New York': [40.7128, -74.0060],
  'Los Angeles': [34.0522, -118.2437],
  'Chicago': [41.8781, -87.6298],
  'London': [51.5074, -0.1278],
  'Singapore': [1.3521, 103.8198],
  'Dubai': [25.2048, 55.2708],
  'Sydney': [-33.8688, 151.2093],
  'Melbourne': [-37.8136, 144.9631],
  'Berlin': [52.5200, 13.4050],
  'Paris': [48.8566, 2.3522],
  'Tokyo': [35.6762, 139.6503],
  // ── Legacy coords (kept so older creator rows still pin correctly) ──
  'Mumbai': [19.0760, 72.8777],
  'Delhi': [28.6139, 77.2090],
  'New Delhi': [28.6139, 77.2090],
  'Bangalore': [12.9716, 77.5946],
  'Bengaluru': [12.9716, 77.5946],
  'Hyderabad': [17.3850, 78.4867],
  'Chennai': [13.0827, 80.2707],
  'Kolkata': [22.5726, 88.3639],
  'Pune': [18.5204, 73.8567],
}

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`
  return String(n)
}

function createCreatorIcon(name: string) {
  const initial = name.charAt(0).toUpperCase()
  return L.divIcon({
    html: `<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#4F46E5,#7C3AED);border:2.5px solid white;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:13px;box-shadow:0 3px 10px rgba(79,70,229,0.45);font-family:Inter,sans-serif;cursor:pointer;">${initial}</div>`,
    className: '',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -20],
  })
}

interface MapViewProps {
  creators: Creator[]
  center?: [number, number]
  zoom?: number
}

export default function MapView({ creators, center, zoom }: MapViewProps) {
  const creatorsWithCoords = creators
    .filter(c => c.city && CITY_COORDS[c.city])
    .map(c => ({ ...c, coords: CITY_COORDS[c.city!] as [number, number] }))

  // Smart default: if any creators are in Toronto, center there at zoom 10.
  // Otherwise center on the first creator's city, or fall back to Toronto.
  const fallbackCenter: [number, number] = CITY_COORDS['Toronto']
  const torontoHas = creatorsWithCoords.some(c => c.city === 'Toronto')
  const inferredCenter =
    center
    ?? (torontoHas ? CITY_COORDS['Toronto']
        : (creatorsWithCoords[0]?.coords ?? fallbackCenter))
  const inferredZoom = zoom ?? (torontoHas ? 10 : 5)

  return (
    <MapContainer
      center={inferredCenter}
      zoom={inferredZoom}
      style={{ height: '100%', width: '100%' }}
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {creatorsWithCoords.map(c => {
        const total = (c.instagram_followers || 0) + (c.tiktok_followers || 0) + (c.youtube_subscribers || 0)
        return (
          <Marker
            key={c.id}
            position={c.coords}
            icon={createCreatorIcon(c.display_name || c.full_name)}
          >
            <Popup>
              <div style={{ minWidth: 190, fontFamily: 'Inter, sans-serif' }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: '#1E1B4B', marginBottom: 3 }}>
                  {c.display_name || c.full_name}
                </div>
                <div style={{ fontSize: 12, color: '#6B7280', marginBottom: 6 }}>
                  📍 {c.city}, {c.country}
                </div>
                <div style={{ fontSize: 12, color: '#374151', marginBottom: 3 }}>
                  👥 {fmt(total)} followers
                </div>
                {c.avg_engagement_rate > 0 && (
                  <div style={{ fontSize: 12, color: '#374151', marginBottom: 6 }}>
                    📈 {c.avg_engagement_rate.toFixed(1)}% engagement
                  </div>
                )}
                {c.niches.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                    {c.niches.slice(0, 3).map(n => (
                      <span
                        key={n}
                        style={{ background: '#EEF2FF', color: '#4F46E5', borderRadius: 999, padding: '2px 8px', fontSize: 11, fontWeight: 600 }}
                      >{n}</span>
                    ))}
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        )
      })}
    </MapContainer>
  )
}

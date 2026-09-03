import React from 'react'
import TemperatureChart from './TemperatureChart'

export default function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>Recorder — Temperature & Humidity</h1>
      </header>
      <main>
        <TemperatureChart />
      </main>
    </div>
  )
}

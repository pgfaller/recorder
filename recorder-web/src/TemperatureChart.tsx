import React, { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'

type Reading = [string, number, number, number]

function formatSeries(data: Reading[]) {
  // sort ascending by timestamp
  const sorted = data.slice().sort((a, b) => a[1] - b[1])
  const times = sorted.map(r => new Date(r[1] * 1000).toISOString())
  const temps = sorted.map(r => r[2])
  const hums = sorted.map(r => r[3])
  return { times, temps, hums }
}

export default function TemperatureChart() {
  const [readings, setReadings] = useState<Reading[]>([])
  const [limit, setLimit] = useState<number>(500)

  useEffect(() => {
    fetch(`/data?limit=${limit}`)
      .then(r => r.json())
      .then((d: Reading[]) => setReadings(d))
      .catch(() => setReadings([]))
  }, [limit])

  const { times, temps, hums } = formatSeries(readings)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperature', 'Humidity'] },
    xAxis: { type: 'category', data: times, boundaryGap: false },
    yAxis: [
      { type: 'value', name: 'Temperature (°C)', position: 'left' },
      { type: 'value', name: 'Humidity (%)', position: 'right' }
    ],
    series: [
      { name: 'Temperature', type: 'line', data: temps, yAxisIndex: 0, smooth: true },
      { name: 'Humidity', type: 'line', data: hums, yAxisIndex: 1, smooth: true }
    ]
  }

  return (
    <div className="chart-container">
      <div className="controls">
        <label>
          Points:
          <select value={limit} onChange={e => setLimit(Number(e.target.value))}>
            <option value={100}>100</option>
            <option value={250}>250</option>
            <option value={500}>500</option>
            <option value={1000}>1000</option>
          </select>
        </label>
      </div>
      <ReactECharts option={option} style={{ height: '480px', width: '100%' }} />
    </div>
  )
}

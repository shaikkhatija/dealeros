import { useEffect, useState } from 'react'
import './App.css'

const REASONS = [
  '',
  'MISSING_IN_B',
  'ORPHAN_IN_B',
  'DUPLICATE_IN_B',
  'VALUE_MISMATCH',
  'LOCATION_MISMATCH',
  'DATE_MISMATCH',
]

function App() {
  const [org, setOrg] = useState('ORG-A')
  const [reason, setReason] = useState('')
  const [sort, setSort] = useState('value')
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    const params = new URLSearchParams({ org, sort })
    if (reason) params.set('reason', reason)
    fetch(`http://localhost:8000/api/disagreements/?${params}`)
      .then((response) => {
        if (!response.ok) throw new Error('Could not load disagreements')
        return response.json()
      })
      .then(setRows)
      .catch((cause) => setError(cause.message))
  }, [org, reason, sort])

  const toggleSort = () => setSort((current) => current === 'value' ? '-value' : 'value')

  return (
    <main>
      <h1>DealerOS reconciliation</h1>
      <div className="controls">
        <label>
          Organization
          <select value={org} onChange={(event) => setOrg(event.target.value)}>
            <option>ORG-A</option>
            <option>ORG-B</option>
          </select>
        </label>
        <label>
          Reason
          <select value={reason} onChange={(event) => setReason(event.target.value)}>
            {REASONS.map((value) => (
              <option key={value} value={value}>{value || 'All reasons'}</option>
            ))}
          </select>
        </label>
      </div>
      {error && <p role="alert">{error}</p>}
      {!error && rows.length === 0 && <p>No disagreements found.</p>}
      {rows.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Reason</th>
              <th>Record ID</th>
              <th>Location</th>
              <th>System A value</th>
              <th>System B value</th>
              <th><button type="button" onClick={toggleSort}>Difference {sort === '-value' ? '▼' : '▲'}</button></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={`${row.record_id}-${row.reason}-${index}`}>
                <td>{row.reason}</td>
                <td>{row.record_id}</td>
                <td>{row.location || ''}</td>
                <td>{row.a_value ?? ''}</td>
                <td>{row.b_value ?? ''}</td>
                <td>{row.difference ?? ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  )
}

export default App

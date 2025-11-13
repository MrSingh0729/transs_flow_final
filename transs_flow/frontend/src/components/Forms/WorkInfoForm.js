import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import api from '../../api';
import { useOffline } from '../../contexts/OfflineContext';
import CameraCapture from '../Camera/CameraCapture';
import BarcodeScanner from '../Scanner/BarcodeScanner';

const WorkInfoForm = () => {
  const { isOnline, saveAction } = useOffline();

  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    shift: '',
    section: '',
    line: '',
    group: '',
    model: '',
    color: '',
  });

  const [suggestions, setSuggestions] = useState({
    lines: [],
    groups: [],
    models: [],
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  // 🔍 Fetch suggestions dynamically from Django endpoints
  const fetchSuggestions = async (type, query) => {
    if (!query || query.length < 1) return;
    try {
      const response = await fetch(`/ipqc/ajax/get-${type}/?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSuggestions((prev) => ({ ...prev, [type + 's']: data }));
    } catch (error) {
      console.error(`Error fetching ${type} suggestions:`, error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Auto-fetch suggestions for dynamic fields
    if (['line', 'group', 'model'].includes(name)) {
      fetchSuggestions(name, value);
    }
  };

  const handleSuggestionClick = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setSuggestions((prev) => ({ ...prev, [field + 's']: [] }));
  };

  const handleScan = (data) => {
    try {
      const parsed = JSON.parse(data);
      setFormData((prev) => ({
        ...prev,
        line: parsed.line || prev.line,
        model: parsed.model || prev.model,
        group: parsed.group || prev.group,
      }));
      toast.success('Scanned data applied!');
    } catch {
      toast.error('Invalid QR data format');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (isOnline) {
        await api.post('/ipqc/api/workinfo/', formData);
        toast.success('Work info submitted successfully!');
      } else {
        await saveAction('/ipqc/api/workinfo/', formData);
        toast.info('Saved locally. Will sync when online.');
      }
      setFormData({
        date: new Date().toISOString().split('T')[0],
        shift: '',
        section: '',
        line: '',
        group: '',
        model: '',
        color: '',
      });
    } catch (error) {
      console.error('Submit error:', error);
      toast.error('Failed to submit. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="work-info-form">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">
          <i className="fas fa-clipboard-list" style={{ color: 'var(--primary)' }}></i>
          Work Information Entry
        </h1>
        <p className="page-subtitle">Record daily manufacturing work details</p>
      </div>

      {/* Form Section */}
      <div className="form-section">
        <h2 className="section-title">
          <i className="fas fa-edit" style={{ color: 'var(--primary)' }}></i>
          Work Details
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Date, Shift */}
          <div className="form-grid">
            <div className="form-group">
              <label><i className="fas fa-calendar"></i> Date</label>
              <input type="date" name="date" value={formData.date} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label><i className="fas fa-clock"></i> Shift</label>
              <select name="shift" value={formData.shift} onChange={handleChange} required>
                <option value="">Select Shift</option>
                <option value="Day">Day</option>
                <option value="Night">Night</option>
              </select>
            </div>
          </div>

          {/* Section, Line, Group */}
          <div className="form-grid">
            <div className="form-group">
              <label><i className="fas fa-industry"></i> Section</label>
              <select name="section" value={formData.section} onChange={handleChange} required>
                <option value="">Select Section</option>
                <option value="Assembly">Assembly</option>
                <option value="NT">NT</option>
                <option value="SMT">SMT</option>
              </select>
            </div>

            <div className="form-group">
              <label><i className="fas fa-sitemap"></i> Line</label>
              <input
                type="text"
                name="line"
                value={formData.line}
                onChange={handleChange}
                placeholder="Type to search line..."
                autoComplete="off"
                required
              />
              {suggestions.lines.length > 0 && (
                <div className="suggestions-box show">
                  {suggestions.lines.map((item, i) => (
                    <div key={i} className="suggestion-item" onClick={() => handleSuggestionClick('line', item)}>
                      {item}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Model, Group, Color */}
          <div className="form-grid">
            <div className="form-group">
              <label><i className="fas fa-users"></i> Group</label>
              <input
                type="text"
                name="group"
                value={formData.group}
                onChange={handleChange}
                placeholder="Type to search group..."
                required
              />
              {suggestions.groups.length > 0 && (
                <div className="suggestions-box show">
                  {suggestions.groups.map((item, i) => (
                    <div key={i} className="suggestion-item" onClick={() => handleSuggestionClick('group', item)}>
                      {item}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="form-group">
              <label><i className="fas fa-cube"></i> Model</label>
              <input
                type="text"
                name="model"
                value={formData.model}
                onChange={handleChange}
                placeholder="Type to search model..."
                required
              />
              {suggestions.models.length > 0 && (
                <div className="suggestions-box show">
                  {suggestions.models.map((item, i) => (
                    <div key={i} className="suggestion-item" onClick={() => handleSuggestionClick('model', item)}>
                      {item}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="form-group">
              <label><i className="fas fa-palette"></i> Color</label>
              <input
                type="text"
                name="color"
                value={formData.color}
                onChange={handleChange}
                placeholder="Enter color code"
                required
              />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="form-section">
            <h3>Quick Actions</h3>
            <div className="quick-actions">
              <BarcodeScanner onScan={handleScan} />
              <CameraCapture />
            </div>
          </div>

          {/* Submit */}
          <div className="submit-section">
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? (
                <span className="loading">
                  <div className="spinner"></div> Submitting...
                </span>
              ) : (
                <>
                  <i className="fas fa-save"></i> Submit Work Info
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default WorkInfoForm;

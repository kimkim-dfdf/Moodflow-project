import { Battery, BatteryLow, BatteryMedium, BatteryFull, Zap } from 'lucide-react';

const EnergySlider = ({ value, onChange }) => {
  const getEnergyLabel = (level) => {
    switch(level) {
      case 1: return 'Very Low';
      case 2: return 'Low';
      case 3: return 'Medium';
      case 4: return 'High';
      case 5: return 'Very High';
      default: return 'Medium';
    }
  };

  const getEnergyIcon = (level) => {
    if (level <= 2) return <BatteryLow size={20} />;
    if (level === 3) return <BatteryMedium size={20} />;
    return <BatteryFull size={20} />;
  };

  const getEnergyColor = (level) => {
    switch(level) {
      case 1: return '#e74c3c';
      case 2: return '#e67e22';
      case 3: return '#f1c40f';
      case 4: return '#2ecc71';
      case 5: return '#27ae60';
      default: return '#f1c40f';
    }
  };

  return (
    <div className="energy-slider-container">
      <div className="energy-header">
        <div className="energy-icon" style={{ color: getEnergyColor(value) }}>
          <Zap size={18} />
        </div>
        <span className="energy-title">Energy Level</span>
        <span className="energy-value" style={{ color: getEnergyColor(value) }}>
          {getEnergyIcon(value)}
          {getEnergyLabel(value)}
        </span>
      </div>
      <div className="energy-slider-wrapper">
        <input
          type="range"
          min="1"
          max="5"
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          className="energy-slider"
          style={{
            background: `linear-gradient(to right, ${getEnergyColor(value)} 0%, ${getEnergyColor(value)} ${(value - 1) * 25}%, #e0e0e0 ${(value - 1) * 25}%, #e0e0e0 100%)`
          }}
        />
        <div className="energy-labels">
          <span>1</span>
          <span>2</span>
          <span>3</span>
          <span>4</span>
          <span>5</span>
        </div>
      </div>
    </div>
  );
};

export default EnergySlider;

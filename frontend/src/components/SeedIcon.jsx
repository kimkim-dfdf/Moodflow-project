const SeedIcon = ({ color = '#22c55e', size = 28 }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <ellipse 
        cx="12" 
        cy="14" 
        rx="6" 
        ry="8" 
        fill={color}
      />
      <path 
        d="M12 6C12 6 14 3 12 1C10 3 12 6 12 6Z" 
        fill={color}
        opacity="0.7"
      />
      <ellipse 
        cx="10" 
        cy="12" 
        rx="2" 
        ry="3" 
        fill="white"
        opacity="0.3"
      />
    </svg>
  );
};

export default SeedIcon;

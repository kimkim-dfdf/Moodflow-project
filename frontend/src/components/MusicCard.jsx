import { Music, ExternalLink } from 'lucide-react';

const MusicCard = ({ music }) => {
  return (
    <div className="music-card">
      <div className="music-icon">
        <Music size={24} />
      </div>
      <div className="music-info">
        <h4 className="music-title">{music.title}</h4>
        <p className="music-artist">{music.artist}</p>
        <span className="music-genre">{music.genre}</span>
      </div>
      <div className="music-links">
        {music.youtube_url && (
          <a 
            href={music.youtube_url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="music-link youtube"
            title="Play on YouTube"
          >
            <ExternalLink size={16} />
            YouTube
          </a>
        )}
      </div>
    </div>
  );
};

export default MusicCard;

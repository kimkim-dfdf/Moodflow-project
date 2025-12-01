/**
 * Dashboard 페이지 컴포넌트
 * - 오늘의 감정 선택 및 기록
 * - 감정 기반 할일 추천
 * - 음악 추천
 * - 미니 캘린더와 감정 통계
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useDate } from '../context/DateContext';
import EmotionSelector from '../components/EmotionSelector';
import TaskCard from '../components/TaskCard';
import MusicCard from '../components/MusicCard';
import MiniCalendar from '../components/MiniCalendar';
import MoodStats from '../components/MoodStats';
import api from '../api/axios';
import { format, isToday } from 'date-fns';
import { Sparkles, Music, CheckCircle2, Calendar } from 'lucide-react';


const Dashboard = () => {
  // 사용자 정보와 선택된 날짜 가져오기
  const { user } = useAuth();
  const { selectedDate, setSelectedDate } = useDate();
  
  // 상태 관리
  const [selectedEmotion, setSelectedEmotion] = useState(null);         // 선택된 감정
  const [recommendedTasks, setRecommendedTasks] = useState([]);         // 추천 할일 목록
  const [suggestedTasks, setSuggestedTasks] = useState([]);             // 제안 할일 목록
  const [musicRecommendations, setMusicRecommendations] = useState([]); // 추천 음악
  const [taskSummary, setTaskSummary] = useState({ total: 0, completed: 0, pending: 0 });
  const [moodStats, setMoodStats] = useState(null);                     // 감정 통계
  const [loading, setLoading] = useState(true);
  const [addedTasks, setAddedTasks] = useState(new Set());              // 이미 추가된 할일 제목들
  const [allTasks, setAllTasks] = useState([]);
  const [calendarRefreshKey, setCalendarRefreshKey] = useState(0);      // 캘린더 새로고침용


  // 날짜가 바뀔 때마다 데이터 새로 불러오기
  useEffect(() => {
    fetchDashboardData();
  }, [selectedDate]);


  // 감정이 선택되면 추천 목록 업데이트
  useEffect(() => {
    if (selectedEmotion) {
      fetchRecommendations(selectedEmotion.name);
    }
  }, [selectedEmotion]);


  /**
   * 대시보드 전체 데이터 가져오기
   * - 요약 정보, 해당 날짜의 감정 기록, 할일 목록
   */
  const fetchDashboardData = async () => {
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      
      // 여러 API를 동시에 호출해서 시간 절약
      const [summaryRes, dateEmotionRes, tasksRes] = await Promise.all([
        api.get('/dashboard/summary', { params: { date: dateStr } }),
        api.get(`/emotions/diary/${dateStr}`),
        api.get('/tasks', { params: { date: dateStr } })
      ]);

      const summary = summaryRes.data;
      setTaskSummary(summary.task_summary);
      setMoodStats(summary.weekly_mood_stats);
      setAllTasks(tasksRes.data);
      
      // 이미 추가된 할일 제목들 저장 (중복 방지용)
      const existingTitles = new Set(tasksRes.data.map(t => t.title));
      setAddedTasks(existingTitles);

      // 해당 날짜에 기록된 감정이 있으면 표시
      if (dateEmotionRes.data && dateEmotionRes.data.emotion) {
        setSelectedEmotion(dateEmotionRes.data.emotion);
      } else {
        // 감정 기록이 없으면 초기화
        setSelectedEmotion(null);
        setRecommendedTasks([]);
        setSuggestedTasks([]);
        setMusicRecommendations([]);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setSelectedEmotion(null);
    } finally {
      setLoading(false);
    }
  };


  /**
   * 감정 기반 추천 데이터 가져오기
   * - 할일 추천, 새 할일 제안, 음악 추천
   */
  const fetchRecommendations = async (emotionName) => {
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      
      const [tasksRes, suggestionsRes, musicRes] = await Promise.all([
        api.get('/tasks/recommended', { 
          params: { emotion: emotionName, limit: 3, date: dateStr } 
        }),
        api.get('/tasks/suggestions', { 
          params: { emotion: emotionName, limit: 3 } 
        }),
        api.get('/music/recommendations', { 
          params: { emotion: emotionName, limit: 4 } 
        })
      ]);

      setRecommendedTasks(tasksRes.data);
      setSuggestedTasks(suggestionsRes.data);
      setMusicRecommendations(musicRes.data);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  };


  /**
   * 할일 완료 상태 토글
   */
  const handleTaskToggle = async (task) => {
    try {
      await api.put(`/tasks/${task.id}`, { 
        is_completed: !task.is_completed 
      });
      
      // 데이터 새로고침
      fetchDashboardData();
      if (selectedEmotion) {
        fetchRecommendations(selectedEmotion.name);
      }
    } catch (error) {
      console.error('Failed to toggle task:', error);
    }
  };


  /**
   * 제안된 할일을 내 할일 목록에 추가
   */
  const handleAddSuggestedTask = async (suggestion) => {
    // 이미 추가된 할일이면 무시
    if (addedTasks.has(suggestion.title)) {
      return;
    }
    
    try {
      const dateStr = format(selectedDate, 'yyyy-MM-dd');
      
      await api.post('/tasks', {
        title: suggestion.title,
        category: suggestion.category,
        priority: suggestion.priority,
        task_date: dateStr,
        recommended_for_emotion: selectedEmotion?.name
      });
      
      // 추가된 할일 목록 업데이트
      setAddedTasks(prev => new Set([...prev, suggestion.title]));
      
      // 데이터 새로고침
      fetchDashboardData();
      if (selectedEmotion) {
        fetchRecommendations(selectedEmotion.name);
      }
    } catch (error) {
      // 이미 존재하는 할일이면 추가된 것으로 표시
      if (error.response?.status === 409) {
        setAddedTasks(prev => new Set([...prev, suggestion.title]));
      }
      console.error('Failed to add task:', error);
    }
  };


  /**
   * 날짜 선택 처리
   */
  const handleDateSelect = (date) => {
    setSelectedDate(date);
    setLoading(true);
  };


  /**
   * 감정 선택 및 저장
   */
  const handleEmotionSelect = async (emotion) => {
    setSelectedEmotion(emotion);
    
    try {
      await api.post('/emotions/record', {
        emotion_id: emotion.id,
        date: format(selectedDate, 'yyyy-MM-dd')
      });
      
      // 캘린더 새로고침 (이모지 업데이트)
      setCalendarRefreshKey(prev => prev + 1);
    } catch (error) {
      console.error('Failed to record emotion:', error);
    }
  };


  /**
   * 시간대에 따른 인사말 반환
   */
  const getGreeting = () => {
    const hour = new Date().getHours();
    
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };


  /**
   * 날짜 표시 문자열 생성
   */
  const getDateDisplay = () => {
    if (isToday(selectedDate)) {
      return format(selectedDate, 'EEEE, MMMM d, yyyy') + ' (Today)';
    }
    return format(selectedDate, 'EEEE, MMMM d, yyyy');
  };


  // 로딩 중일 때 표시
  if (loading) {
    return <div className="loading-screen">Loading your dashboard...</div>;
  }


  return (
    <div className="dashboard-page">
      {/* 헤더 영역 - 인사말과 할일 요약 */}
      <header className="dashboard-header">
        <div className="greeting">
          <h1>{getGreeting()}, {user?.username}!</h1>
          <p className="date-display">
            <Calendar size={16} />
            {getDateDisplay()}
          </p>
          {!isToday(selectedDate) && (
            <button 
              className="today-btn"
              onClick={() => handleDateSelect(new Date())}
            >
              Back to Today
            </button>
          )}
        </div>
        
        {/* 할일 요약 배지들 */}
        <div className="task-summary-badges">
          <div className="badge total">
            <span className="badge-value">{taskSummary.total}</span>
            <span className="badge-label">Total Tasks</span>
          </div>
          <div className="badge completed">
            <CheckCircle2 size={16} />
            <span className="badge-value">{taskSummary.completed}</span>
            <span className="badge-label">Completed</span>
          </div>
          <div className="badge pending">
            <span className="badge-value">{taskSummary.pending}</span>
            <span className="badge-label">Pending</span>
          </div>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* 메인 콘텐츠 영역 */}
        <div className="dashboard-main">
          {/* 감정 선택 섹션 */}
          <section className="card emotion-section">
            <div className="emotion-header">
              <h3>How are you feeling {isToday(selectedDate) ? 'today' : 'on this day'}?</h3>
              {!selectedEmotion && (
                <p className="emotion-hint">Select your mood to get personalized recommendations</p>
              )}
            </div>
            <EmotionSelector 
              selectedEmotion={selectedEmotion} 
              onSelect={handleEmotionSelect}
              selectedDate={selectedDate}
            />
          </section>

          {/* 감정이 선택되면 추천 섹션들 표시 */}
          {selectedEmotion && (
            <>
              {/* 추천 할일 섹션 */}
              <section className="card recommendations-section">
                <div className="section-header">
                  <h3><Sparkles size={20} /> Recommended Tasks for You</h3>
                </div>
                {recommendedTasks.length > 0 ? (
                  <div className="task-list">
                    {recommendedTasks.map((item) => (
                      <TaskCard 
                        key={item.task.id} 
                        task={{ ...item.task, score: item.score }} 
                        onToggle={handleTaskToggle}
                        showScore={true}
                        selectedDate={selectedDate}
                      />
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">No tasks yet. Add some tasks to get personalized recommendations!</p>
                )}
              </section>

              {/* 할일 제안 섹션 */}
              <section className="card suggestions-section">
                <div className="section-header">
                  <h3>Suggested Activities for {selectedEmotion.name} Mood</h3>
                </div>
                <div className="suggestions-grid">
                  {suggestedTasks.map((suggestion, index) => {
                    const isAdded = addedTasks.has(suggestion.title);
                    return (
                      <div key={index} className="suggestion-card">
                        <p>{suggestion.title}</p>
                        <div className="suggestion-meta">
                          <span className="category">{suggestion.category}</span>
                          <button 
                            className={`add-btn ${isAdded ? 'added' : ''}`}
                            onClick={() => handleAddSuggestedTask(suggestion)}
                            disabled={isAdded}
                          >
                            {isAdded ? 'Added' : 'Add to Tasks'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>

              {/* 음악 추천 섹션 */}
              <section className="card music-section">
                <div className="section-header">
                  <h3><Music size={20} /> Music for Your Mood</h3>
                </div>
                <div className="music-grid">
                  {musicRecommendations.map((music) => (
                    <MusicCard key={music.id} music={music} />
                  ))}
                </div>
              </section>
            </>
          )}
        </div>

        {/* 사이드바 영역 */}
        <aside className="dashboard-sidebar">
          {/* 미니 캘린더 */}
          <section className="card calendar-section">
            <h3 className="calendar-title">Select a Date</h3>
            <MiniCalendar 
              key={calendarRefreshKey}
              onDateSelect={handleDateSelect}
              selectedDate={selectedDate}
            />
          </section>

          {/* 감정 통계 */}
          <section className="card stats-section">
            <MoodStats stats={moodStats} />
          </section>
        </aside>
      </div>
    </div>
  );
};

export default Dashboard;

import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useLocation, Link } from 'react-router-dom';
import {
  Home,
  MicVocal,
  Joystick,
  LayoutList,
  MessageSquare,
  ShoppingBag,
  Package,
  Map,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Video as VideoIcon,
  ClipboardList, // 🔹 Ajouté ici
} from 'lucide-react';

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const menuItems = [
    { icon: Home, label: 'Overview', path: '/' },
    { icon: LayoutList, label: 'Behaviors', path: '/behaviors' },
    { icon: MessageSquare, label: 'Chat', path: '/dialog' },
    { icon: MicVocal, label: 'Quiz', path: '/quiz' },
    { icon: Joystick, label: 'Déplacer', path: '/move' },
    { icon: Map, label: 'Navigation', path: '/slam' },
    { icon: VideoIcon, label: 'Vidéo', path: '/video' },
    { icon: ClipboardList, label: 'Total Santé', path: '/totalSante' }, // ✅ Nouveau
    { icon: Settings, label: 'Settings', path: '/settings' },
    
  ];

  return (
    <div className="d-flex position-relative">
      <div
        className={`bg-dark text-white vh-100 d-flex flex-column justify-content-between ${
          collapsed ? 'align-items-center' : ''
        } py-4`}
        style={{
          width: collapsed ? '4rem' : '12rem',
          transition: 'width 0.3s ease-in-out',
        }}
      >
        <div>
          {menuItems.map((item, index) => (
            <Link to={item.path} key={index} className="text-white text-decoration-none">
              <div
                className={`my-3 position-relative cursor-pointer d-flex align-items-center ${
                  collapsed ? 'justify-content-center' : 'ms-3'
                }`}
              >
                <item.icon />
                {!collapsed && <span className="ms-3">{item.label}</span>}
                {item.notification && (
                  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                    {item.notification}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>

        <div className="d-flex flex-column align-items-center w-100">
      <button
        className="btn position-absolute border-0 d-flex align-items-center justify-content-center"
        style={{ 
          bottom: '2rem',
          left: collapsed ? '4rem' : '12rem',
          transform: 'translateX(-60%)',
          transition: 'left 0.3s ease-in-out, transform 0.3s ease-in-out',
          zIndex: 10,
          borderRadius: '50%',
          backgroundColor: '#212529',
          color: 'white',
          width: '2.5rem',
          height: '2.5rem'
        }}
        onClick={() => setCollapsed(!collapsed)}
      >
        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
      </button>
        </div>
      </div>
    </div>
  );
}

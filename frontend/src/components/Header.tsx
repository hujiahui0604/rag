import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import { FileText, MessageCircle, Settings, LogOut, User } from 'lucide-react';

export function Header() {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <header className="border-b bg-white">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-8">
          <Link to="/" className="text-xl font-bold text-primary">
            企业知识库
          </Link>
          <nav className="flex items-center gap-6">
            <Link
              to="/documents"
              className={`flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary ${
                location.pathname.startsWith('/documents') ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              <FileText className="h-4 w-4" />
              文档管理
            </Link>
            <Link
              to="/chat"
              className={`flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary ${
                location.pathname === '/chat' ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              <MessageCircle className="h-4 w-4" />
              智能问答
            </Link>
            {user?.role === 'admin' && (
              <Link
                to="/admin"
                className={`flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary ${
                  location.pathname === '/admin' ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                <Settings className="h-4 w-4" />
                管理面板
              </Link>
            )}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <User className="h-4 w-4" />
            <span>{user?.username}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            退出
          </Button>
        </div>
      </div>
    </header>
  );
}
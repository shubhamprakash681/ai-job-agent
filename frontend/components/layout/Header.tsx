'use client';

import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { LogOut, User as UserIcon } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  
  const title = pathname.split('/')[1] || 'Dashboard';
  const displayTitle = title.charAt(0).toUpperCase() + title.slice(1);

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <h2 className="text-xl font-semibold text-gray-800">{displayTitle}</h2>
      
      <div className="flex items-center space-x-4">
        <div className="flex items-center text-gray-600">
          <UserIcon className="h-5 w-5 mr-2" />
          <span className="text-sm font-medium">{user?.full_name || user?.email || 'User'}</span>
        </div>
        <button
          onClick={logout}
          className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
          title="Logout"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}

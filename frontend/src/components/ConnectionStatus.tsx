import React, { useState, useEffect, useCallback } from 'react';
import { AlertCircle, CheckCircle, Wifi, WifiOff } from 'lucide-react';

interface ConnectionStatusProps {
  className?: string;
  showText?: boolean;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  className = '', 
  showText = true 
}) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  // Check backend connectivity
  const checkBackendConnection = async (): Promise<boolean> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('/api/v1/health/', {
        method: 'GET',
        signal: controller.signal,
        cache: 'no-cache'
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  };

  // Update backend status
  const updateBackendStatus = useCallback(async () => {
    if (!isOnline) {
      setBackendStatus('disconnected');
      return;
    }

    setBackendStatus('checking');
    const isConnected = await checkBackendConnection();
    setBackendStatus(isConnected ? 'connected' : 'disconnected');
    setLastChecked(new Date());
  }, [isOnline]);

  // Handle network status changes
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      updateBackendStatus();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setBackendStatus('disconnected');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initial check
    updateBackendStatus();

    // Periodic health checks every 30 seconds
    const interval = setInterval(updateBackendStatus, 30000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, [isOnline, updateBackendStatus]);

  // Get status display properties
  const getStatusDisplay = () => {
    if (!isOnline) {
      return {
        icon: WifiOff,
        color: 'text-red-500',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        text: 'Offline',
        description: 'No internet connection'
      };
    }

    switch (backendStatus) {
      case 'connected':
        return {
          icon: CheckCircle,
          color: 'text-green-500',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          text: 'Connected',
          description: 'Server is available'
        };
      case 'disconnected':
        return {
          icon: AlertCircle,
          color: 'text-red-500',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          text: 'Server Unavailable',
          description: 'Cannot connect to server'
        };
      case 'checking':
        return {
          icon: Wifi,
          color: 'text-yellow-500',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          text: 'Checking...',
          description: 'Checking server status'
        };
    }
  };

  const status = getStatusDisplay();
  const Icon = status.icon;

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${status.bgColor} ${status.borderColor} ${className}`}>
      <Icon className={`h-4 w-4 ${status.color}`} />
      {showText && (
        <div className="flex flex-col">
          <span className={`text-sm font-medium ${status.color}`}>
            {status.text}
          </span>
          {lastChecked && backendStatus !== 'checking' && (
            <span className="text-xs text-gray-500">
              Last checked: {lastChecked.toLocaleTimeString()}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;
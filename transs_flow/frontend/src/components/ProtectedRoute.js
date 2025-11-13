import React from 'react';
import { useOffline } from '../contexts/OfflineContext';
 
const OfflineBanner = () => {
  const { isOnline, syncStatus, pendingActions } = useOffline();
  
  if (isOnline) return null;
  
  return (
    <div className="offline-banner">
      <div className="container mx-auto px-4 py-2 bg-yellow-500 text-white text-center">
        <i className="fas fa-wifi-slash mr-2"></i>
        You are offline. Changes are being saved locally.
        {pendingActions.length > 0 && (
          <span className="ml-2">
            ({pendingActions.length} pending actions)
          </span>
        )}
      </div>
    </div>
  );
};
 
export default OfflineBanner;
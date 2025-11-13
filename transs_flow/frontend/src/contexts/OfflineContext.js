import React, { createContext, useContext, useState, useEffect } from 'react';
import { openDB } from 'dexie';
import { toast } from 'react-toastify';
 
const OfflineContext = createContext();
 
export const useOffline = () => {
  return useContext(OfflineContext);
};
 
export const OfflineProvider = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [syncStatus, setSyncStatus] = useState('idle');
  const [pendingActions, setPendingActions] = useState([]);
 
  // Initialize IndexedDB
  useEffect(() => {
    const initDB = async () => {
      const db = await openDB('ipqc-queue', 1, {
        upgrade(db) {
          db.createObjectStore('actions', { keyPath: 'id', autoIncrement: true });
          db.createObjectStore('forms', { keyPath: 'id', autoIncrement: true });
        }
      });
      return db;
    };
 
    initDB();
  }, []);
 
  // Online/Offline detection
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success('You are back online!');
      syncPendingActions();
    };
 
    const handleOffline = () => {
      setIsOnline(false);
      toast.warn('You are offline. Actions will be saved locally.');
    };
 
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
 
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
 
  // Save action to IndexedDB
  const saveAction = async (action) => {
    try {
      const db = await openDB('ipqc-queue', 1);
      await db.put('actions', {
        ...action,
        timestamp: Date.now(),
        status: 'pending'
      });
      
      setPendingActions(prev => [...prev, action]);
      return true;
    } catch (error) {
      console.error('Error saving action:', error);
      return false;
    }
  };
 
  // Sync pending actions
  const syncPendingActions = async () => {
    if (!isOnline) return;
    
    setSyncStatus('syncing');
    try {
      const db = await openDB('ipqc-queue', 1);
      const allActions = await db.getAll('actions');
      
      for (const action of allActions) {
        try {
          await axios.post(action.endpoint, action.data, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          
          // Mark as synced
          await db.put('actions', { ...action, status: 'synced' });
          
          // Remove from state
          setPendingActions(prev => prev.filter(a => a.id !== action.id));
        } catch (error) {
          console.error('Sync failed for action:', action.id);
          // Keep as pending
        }
      }
      
      setSyncStatus('idle');
      if (allActions.length > 0) {
        toast.success(`Synced ${allActions.length} actions`);
      }
    } catch (error) {
      console.error('Sync error:', error);
      setSyncStatus('error');
      toast.error('Sync failed. Please try again.');
    }
  };
 
  // Clear synced actions
  const clearSyncedActions = async () => {
    try {
      const db = await openDB('ipqc-queue', 1);
      await db.clear('actions');
      setPendingActions([]);
    } catch (error) {
      console.error('Error clearing synced actions:', error);
    }
  };
 
  const value = {
    isOnline,
    syncStatus,
    pendingActions,
    saveAction,
    syncPendingActions,
    clearSyncedActions
  };
 
  return (
    <OfflineContext.Provider value={value}>
      {children}
    </OfflineContext.Provider>
  );
};
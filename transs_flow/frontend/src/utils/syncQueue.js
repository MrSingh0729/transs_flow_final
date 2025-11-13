import api from '../api';
import { getPendingActions, updateActionStatus, deleteAction } from '../utils/indexedDB';
 
// Sync all pending actions
export const syncPendingActions = async () => {
  const actions = await getPendingActions();
  
  for (const action of actions) {
    try {
      // Send action to server
      const response = await api.post(action.endpoint, action.data);
      
      // Update status to synced
      await updateActionStatus(action.id, 'synced');
      
      // Remove from IndexedDB after successful sync
      await deleteAction(action.id);
      
      console.log(`Synced action ${action.id}`);
    } catch (error) {
      console.error(`Failed to sync action ${action.id}:`, error);
      // Keep as pending for next sync attempt
      await updateActionStatus(action.id, 'failed');
    }
  }
};
 
// Queue an action for syncing
export const queueAction = async (endpoint, data) => {
  // Save to IndexedDB first
  const db = await openDB('ipqc-queue', 1);
  const action = await db.put('actions', {
    endpoint,
    data,
    timestamp: Date.now(),
    status: 'pending'
  });
  
  // If online, try to sync immediately
  if (navigator.onLine) {
    try {
      const response = await api.post(endpoint, data);
      
      // If successful, remove from queue
      await deleteAction(action.id);
      return response;
    } catch (error) {
      console.error('Immediate sync failed:', error);
      // Will be retried later
    }
  }
  
  return action;
};
 
// Retry failed actions
export const retryFailedActions = async () => {
  const db = await openDB('ipqc-queue', 1);
  const failedActions = await db.getAll('actions');
  
  for (const action of failedActions) {
    if (action.status === 'failed') {
      try {
        await api.post(action.endpoint, action.data);
        await deleteAction(action.id);
        console.log(`Retried and synced action ${action.id}`);
      } catch (error) {
        console.error(`Retry failed for action ${action.id}:`, error);
      }
    }
  }
};
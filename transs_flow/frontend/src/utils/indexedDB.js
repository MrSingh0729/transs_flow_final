	import { openDB } from 'dexie';
 
// Initialize IndexedDB
export const initDB = async () => {
  const db = await openDB('ipqc-queue', 1, {
    upgrade(db) {
      // Create stores for different data types
      db.createObjectStore('actions', { keyPath: 'id', autoIncrement: true });
      db.createObjectStore('forms', { keyPath: 'id', autoIncrement: true });
      db.createObjectStore('media', { keyPath: 'id', autoIncrement: true });
      db.createObjectStore('settings', { keyPath: 'key' });
    }
  });
  return db;
};
 
// Save action to queue
export const saveAction = async (action) => {
  const db = await openDB('ipqc-queue', 1);
  return await db.put('actions', {
    ...action,
    timestamp: Date.now(),
    status: 'pending'
  });
};
 
// Get all pending actions
export const getPendingActions = async () => {
  const db = await openDB('ipqc-queue', 1);
  return await db.getAll('actions');
};
 
// Update action status
export const updateActionStatus = async (id, status) => {
  const db = await openDB('ipqc-queue', 1);
  const action = await db.get('actions', id);
  if (action) {
    return await db.put('actions', { ...action, status });
  }
  return null;
};
 
// Delete action
export const deleteAction = async (id) => {
  const db = await openDB('ipqc-queue', 1);
  return await db.delete('actions', id);
};
 
// Save form data
export const saveFormData = async (formId, data) => {
  const db = await openDB('ipqc-queue', 1);
  return await db.put('forms', {
    formId,
    data,
    timestamp: Date.now(),
    status: 'pending'
  });
};
 
// Get form data
export const getFormData = async (formId) => {
  const db = await openDB('ipqc-queue', 1);
  return await db.get('forms', formId);
};
 
// Save media file
export const saveMediaFile = async (file, metadata) => {
  const db = await openDB('ipqc-queue', 1);
  return await db.put('media', {
    file,
    metadata,
    timestamp: Date.now(),
    status: 'pending'
  });
};
 
// Get media files
export const getMediaFiles = async () => {
  const db = await openDB('ipqc-queue', 1);
  return await db.getAll('media');
};
 
// Save settings
export const saveSetting = async (key, value) => {
  const db = await openDB('ipqc-queue', 1);
  return await db.put('settings', { key, value });
};
 
// Get setting
export const getSetting = async (key) => {
  const db = await openDB('ipqc-queue', 1);
  const setting = await db.get('settings', key);
  return setting ? setting.value : null;
};
 
// Clear all data
export const clearAllData = async () => {
  const db = await openDB('ipqc-queue', 1);
  await db.clear('actions');
  await db.clear('forms');
  await db.clear('media');
  await db.clear('settings');
};
import imageCompression from 'browser-image-compression';
 
export const compressImage = async (file, options = {}) => {
  const defaultOptions = {
    maxSizeMB: 1,
    maxWidthOrHeight: 1920,
    useWebWorker: true,
    ...options
  };
  
  try {
    const compressedFile = await imageCompression(file, defaultOptions);
    return compressedFile;
  } catch (error) {
    console.error('Error compressing image:', error);
    return file; // Return original file if compression fails
  }
};
 
export const compressImages = async (files, options = {}) => {
  const compressedFiles = [];
  
  for (const file of files) {
    if (file.type.startsWith('image/')) {
      const compressedFile = await compressImage(file, options);
      compressedFiles.push(compressedFile);
    } else {
      compressedFiles.push(file);
    }
  }
  
  return compressedFiles;
};
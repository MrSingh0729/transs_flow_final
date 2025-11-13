import api from './index';

const BASE = '/qa/api';

// Work Info
export const getWorkInfo = () => api.get(`${BASE}/workinfo/`);
export const getWorkInfoById = (id) => api.get(`${BASE}/workinfo/${id}/`);
export const createWorkInfo = (data) => api.post(`${BASE}/workinfo/`, data);

// FAI
export const getFAIList = () => api.get(`${BASE}/fai/`);
export const createFAI = (data) => api.post(`${BASE}/fai/`, data);

// Assembly Audit
export const getAssemblyAudits = () => api.get('/ipqc/api/audit/');
export const createAssemblyAudit = (data) => api.post('/ipqc/api/audit/', data);

// BTB Checksheet
export const getBTBChecksheets = () => api.get('/ipqc/api/btb/');
export const createBTBChecksheet = (data) => api.post('/ipqc/api/btb/', data);

// Disassemble
export const getDisassembleList = () => api.get('/ipqc/api/disassemble/');
export const createDisassembleEntry = (data) => api.post('/ipqc/api/disassemble/', data);

// NC Issue Tracking
export const getNCIssues = () => api.get('/ipqc/api/nc-issue/');
export const createNCIssue = (data) => api.post('/ipqc/api/nc-issue/', data);

// ESD Compliance
export const getESDChecklists = () => api.get('/ipqc/api/esd/');
export const createESDChecklist = (data) => api.post('/ipqc/api/esd/', data);

// Operator Qualification
export const getOperatorQualList = () => api.get('/ipqc/api/operator-qual/');
export const createOperatorQual = (data) => api.post('/ipqc/api/operator-qual/', data);

// Dust Count
export const getDustCountList = () => api.get('/ipqc/api/dust-count/');
export const createDustCountEntry = (data) => api.post('/ipqc/api/dust-count/', data);

// Dynamic Forms
export const getDynamicForms = () => api.get('/ipqc/api/dynamic-forms/');
export const submitDynamicForm = (data) => api.post('/ipqc/api/dynamic-forms/', data);

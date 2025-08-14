import axios from './axios';
import useAxios from './useAxios';

// API Configuration endpoints
export const getApiConfig = () => {
    const api = useAxios();
    return api.get('config/');
};
export const updateApiConfig = (data) => {
    const api = useAxios();
    return api.post('config/', data);
};
export const clearApiConfig = () => {
    const api = useAxios();
    return api.post('clear-config/');
};

// Assistant endpoints
export const createAssistant = (data) => {
    const api = useAxios();
    return api.post('create-assistant/', data);
};
export const getAssistants = (campaignId = null) => {
    const api = useAxios();
    const params = campaignId ? { campaign_id: campaignId } : {};
    return api.get('assistants/', { params });
};

// Phone number endpoints
export const getVapiPhoneNumbers = () => {
    const api = useAxios();
    return api.get('phone-numbers/');
};
export const getTwilioPhoneNumbers = () => {
    const api = useAxios();
    return api.get('twilio-numbers/');
};
export const registerPhoneNumber = (phoneNumber, campaignId = null) => {
    const api = useAxios();
    const data = { phone_number: phoneNumber };
    if (campaignId) {
        data.campaign_id = campaignId;
    }
    return api.post('register-phone-number/', data);
};
export const getMyPhoneNumbers = (campaignId = null) => {
    const api = useAxios();
    const params = campaignId ? { campaign_id: campaignId } : {};
    return api.get('my-phone-numbers/', { params });
};

// Call endpoints
export const makeCall = (data) => {
    const api = useAxios();
    return api.post('make-call/', data);
};
export const getCallDetails = (callId) => {
    const api = useAxios();
    return api.get(`call/${callId}/`);
};
export const getCalls = (campaignId = null) => {
    const api = useAxios();
    const params = campaignId ? { campaign_id: campaignId } : {};
    return api.get('calls/', { params });
};

// Scheduled call endpoints
export const scheduleCall = (data) => {
    const api = useAxios();
    return api.post('schedule-call/', data);
};
export const getScheduledCalls = (campaignId = null) => {
    const api = useAxios();
    const params = campaignId ? { campaign_id: campaignId } : {};
    return api.get('scheduled-calls/', { params });
};
export const getScheduledCallDetails = (callId) => {
    const api = useAxios();
    return api.get(`scheduled-call/${callId}/`);
};
export const updateScheduledCall = (callId, data) => {
    const api = useAxios();
    return api.patch(`scheduled-call/${callId}/`, data);
};
export const deleteScheduledCall = (callId) => {
    const api = useAxios();
    return api.delete(`scheduled-call/${callId}/`);
};

// Website Analysis
export const analyzeWebsite = (websiteUrl) => {
    const api = useAxios();
    return api.post('analyze-website/', { website_url: websiteUrl });
};
export const executeScheduledCalls = () => {
    const api = useAxios();
    return api.post('execute-scheduled-calls/');
};

// Test endpoint
export const testEndpoint = (data) => {
    const api = useAxios();
    return api.post('test/', data);
};

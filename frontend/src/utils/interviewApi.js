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
export const getAssistants = () => {
    const api = useAxios();
    return api.get('assistants/');
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
export const registerPhoneNumber = (phoneNumber) => {
    const api = useAxios();
    return api.post('register-phone-number/', { phone_number: phoneNumber });
};
export const getMyPhoneNumbers = () => {
    const api = useAxios();
    return api.get('my-phone-numbers/');
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
export const getCalls = () => {
    const api = useAxios();
    return api.get('calls/');
};

// Test endpoint
export const testEndpoint = (data) => {
    const api = useAxios();
    return api.post('test/', data);
};

import useAxios from './useAxios';

export async function getCampaigns() {
    const api = useAxios();
    return api.get('campaign/');
}

export const createCampaigns = (data) => {
    const api = useAxios();
    return api.post('campaign/', data);
};

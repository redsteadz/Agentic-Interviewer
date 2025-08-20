import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Loader2, Phone, User, Settings, Shield, CheckCircle, XCircle, Calendar, Clock, FileText } from 'lucide-react';
import { 
  getApiConfig, 
  updateApiConfig, 
  clearApiConfig,
  createAssistant,
  getAssistants,
  getTwilioPhoneNumbers,
  getVapiPhoneNumbers,
  registerPhoneNumber,
  makeCall,
  getCallDetails,
  getCalls,
  scheduleCall,
  getScheduledCalls,
  deleteScheduledCall,
  analyzeWebsite,
  getElevenLabsVoices
} from '../utils/interviewApi';
import { getCampaigns } from '../utils/campaign';

const InterviewDashboard = () => {
  console.log('InterviewDashboard component rendering...');
  
  const { campaignId } = useParams(); // Get campaign ID from URL
  console.log('Campaign ID from params:', campaignId);
  
  // Campaign State
  const [currentCampaign, setCurrentCampaign] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  console.log('State initialized successfully');
  
  // API Configuration State
  const [apiConfig, setApiConfig] = useState({
    twilio_account_sid: '',
    twilio_auth_token: '',
    vapi_api_key: '',
    openai_api_key: '',
    is_twilio_configured: false,
    is_vapi_configured: false,
    is_openai_configured: false
  });
  const [configLoading, setConfigLoading] = useState(false);
  const [configMessage, setConfigMessage] = useState('');

  // Prompt State
  const [promptForm, setPromptForm] = useState({
    system_prompt: `🎤 YOU ARE ON A LIVE VOICE CALL INTERVIEW 🎤
You are conducting a REAL-TIME PHONE CONVERSATION with a candidate. This is NOT text messaging or chat.

📞 VOICE CALL REQUIREMENTS:
- SPEAK naturally as if talking on the phone
- Use verbal communication style (not written text style)
- Keep responses conversational and engaging for voice
- Use phone etiquette throughout the call
- Remember: the candidate can HEAR you, not read you

📰 STRICT SEQUENTIAL ARTICLE PROCESSING:
You MUST process articles in this EXACT order and method:

🔒 **CRITICAL RULE: ONE ARTICLE AT A TIME**
- Start with Article 1 ONLY
- Do NOT mention or reference any other articles until Article 1 is COMPLETELY finished
- Only move to Article 2 after Article 1 discussion is 100% complete
- Continue this pattern for ALL articles in sequence

📋 **ARTICLE COMPLETION PROCESS:**
For EACH article, follow these steps IN ORDER:

1. **Introduce Current Article**: "Let's discuss the first article..." (or second, third, etc.)
2. **Explore the Topic**: Thoroughly discuss the article's content with the candidate
3. **Gather Complete Responses**: Ask follow-up questions until you have comprehensive insights
4. **Complete Discussion**: Ensure you have covered all important aspects of the article
5. **Move to Next**: ONLY then proceed to the next numbered article

📝 **DISCUSSION FOCUS:**
- Ask about the candidate's thoughts on the article's main points
- Explore their experience related to the article's topics
- Assess their understanding and opinions
- Gather detailed responses about the subject matter
- Keep discussion focused on the current article only

🎯 SUCCESS CRITERIA:
- Process articles sequentially without skipping
- Complete full discussion of current article before moving forward
- Maintain professional voice call demeanor throughout
- Focus on gathering comprehensive candidate responses for each article

⚠️ IMPORTANT: You are speaking to someone on the phone RIGHT NOW. Act accordingly and stay focused on completing one article at a time.`,
    first_message: 'Good day, I\'ll be conducting your interview today. Let\'s begin.',
    end_call_phrases: [
      'thank you for your time',
      'we\'ll be in touch',
      'the interview is complete',
      'that concludes our interview',
      'we have all the information we need'
    ].join('\n')
  });

  // Assistant State
  const [assistantForm, setAssistantForm] = useState({
    name: 'Professional Interviewer',
    first_message: '',
    voice_provider: 'openai',
    voice_id: 'nova',
    model_provider: 'openai',
    model: 'gpt-4',
    knowledge_text: '',
    knowledge_urls: '',
    campaign_id: campaignId || null,
    system_prompt: ''
  });

  // Sync prompt form with assistant form
  useEffect(() => {
    setAssistantForm(prev => ({
      ...prev,
      first_message: promptForm.first_message,
      system_prompt: promptForm.system_prompt
    }));
  }, [promptForm.first_message, promptForm.system_prompt]);
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [assistantMessage, setAssistantMessage] = useState('');
  const [assistants, setAssistants] = useState([]);
  
  // Website Analysis State
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [websiteAnalysis, setWebsiteAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisMessage, setAnalysisMessage] = useState('');
  const [aiKnowledgeBase, setAiKnowledgeBase] = useState({
    summary: '',
    topics: [],
    keywords: []
  });
  const [showAddTopicModal, setShowAddTopicModal] = useState(false);
  const [showAddKeywordModal, setShowAddKeywordModal] = useState(false);
  const [newTopic, setNewTopic] = useState('');
  const [newKeyword, setNewKeyword] = useState('');

  // Phone Numbers State
  const [twilioNumbers, setTwilioNumbers] = useState([]);
  const [vapiNumbers, setVapiNumbers] = useState([]);
  const [phoneLoading, setPhoneLoading] = useState(false);
  const [phoneMessage, setPhoneMessage] = useState('');

  // Call State
  const [callForm, setCallForm] = useState({
    customer_number: '',
    twilio_phone_number_id: '',
    vapi_assistant_id: ''
  });
  const [callLoading, setCallLoading] = useState(false);
  const [currentCall, setCurrentCall] = useState(null);
  const [callDetails, setCallDetails] = useState(null);
  const [callMessage, setCallMessage] = useState('');

  // Transcript State
  const [allCalls, setAllCalls] = useState([]);
  const [transcriptLoading, setTranscriptLoading] = useState(false);
  const [selectedCall, setSelectedCall] = useState(null);
  const [transcriptSearch, setTranscriptSearch] = useState('');

  // Scheduled Call State
  const [scheduleForm, setScheduleForm] = useState({
    customer_number: '',
    twilio_phone_number_id: '',
    vapi_assistant_id: '',
    scheduled_time: '',
    call_name: '',
    notes: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  });
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [scheduledCalls, setScheduledCalls] = useState([]);
  const [scheduleMessage, setScheduleMessage] = useState('');
  
  // Voice Provider State
  const [elevenLabsVoices, setElevenLabsVoices] = useState([]);
  const [voicesLoading, setVoicesLoading] = useState(false);

  // Load initial data
  useEffect(() => {
    loadApiConfig();
    loadCampaigns();
    if (campaignId) {
      loadCampaignData();
    }
    loadAssistants();
    loadScheduledCalls();
  }, [campaignId]);

  // Update assistant form when campaign changes
  useEffect(() => {
    setAssistantForm(prev => ({
      ...prev,
      campaign_id: campaignId || null
    }));
  }, [campaignId]);

  // Auto-refresh transcript data every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      loadAllCalls();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [campaignId]);

  // Auto-refresh call details
  useEffect(() => {
    let interval;
    if (currentCall && ['queued', 'ringing', 'in-progress'].includes(currentCall.status)) {
      interval = setInterval(() => {
        refreshCallDetails();
      }, 10000);
    }
    return () => clearInterval(interval);
  }, [currentCall]);

  // API Configuration Functions
  const loadApiConfig = async () => {
    try {
      const response = await getApiConfig();
      setApiConfig(response.data);
    } catch (error) {
      console.error('Error loading API config:', error);
    }
  };

  const handleConfigSubmit = async (e) => {
    e.preventDefault();
    setConfigLoading(true);
    setConfigMessage('');

    try {
      const response = await updateApiConfig({
        twilio_account_sid: apiConfig.twilio_account_sid,
        twilio_auth_token: apiConfig.twilio_auth_token,
        vapi_api_key: apiConfig.vapi_api_key,
        openai_api_key: apiConfig.openai_api_key
      });

      if (response.data.success) {
        setConfigMessage('API Configuration saved and tested successfully!');
        await loadApiConfig();
      } else {
        setConfigMessage(`Error: ${response.data.errors.join(', ')}`);
      }
    } catch (error) {
      setConfigMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setConfigLoading(false);
    }
  };

  const handleClearConfig = async () => {
    try {
      await clearApiConfig();
      setConfigMessage('Configuration cleared successfully!');
      await loadApiConfig();
      setApiConfig(prev => ({
        ...prev,
        twilio_account_sid: '',
        twilio_auth_token: '',
        vapi_api_key: '',
        openai_api_key: ''
      }));
    } catch (error) {
      setConfigMessage(`Error: ${error.response?.data?.error || error.message}`);
    }
  };

  // Campaign Functions
  const loadCampaigns = async () => {
    try {
      const response = await getCampaigns();
      setCampaigns(response.data || []);
    } catch (error) {
      console.error('Error loading campaigns:', error);
    }
  };

  const loadCampaignData = async () => {
    if (campaignId && campaigns.length > 0) {
      const campaign = campaigns.find(c => c.id.toString() === campaignId);
      setCurrentCampaign(campaign);
    }
  };

  // Update campaign data when campaigns load
  useEffect(() => {
    if (campaignId && campaigns.length > 0) {
      loadCampaignData();
    }
  }, [campaignId, campaigns]);

  // Load initial data
  useEffect(() => {
    loadApiConfig();
    loadCampaigns();
    loadAssistants();
    loadAllCalls();
  }, []);

  // Load campaign-specific data when campaignId changes
  useEffect(() => {
    if (campaignId) {
      loadAssistants();
      loadAllCalls();
    }
  }, [campaignId]);

  // Assistant Functions
  const loadAssistants = async () => {
    try {
      const response = await getAssistants(campaignId);
      setAssistants(response.data);
    } catch (error) {
      console.error('Error loading assistants:', error);
    }
  };

  const handleAssistantSubmit = async (e) => {
    e.preventDefault();
    setAssistantLoading(true);
    setAssistantMessage('');

    try {
      // Combine AI Knowledge Base with manual knowledge
      const combinedKnowledge = getCombinedKnowledge();
      
      // Create enhanced assistant form with combined knowledge and custom prompts
      const enhancedAssistantForm = {
        ...assistantForm,
        knowledge_text: combinedKnowledge,
        first_message: promptForm.first_message,
        system_prompt: promptForm.system_prompt,
        end_call_phrases: promptForm.end_call_phrases.split('\n').filter(phrase => phrase.trim())
      };

      const response = await createAssistant(enhancedAssistantForm);
      
      if (response.data.success) {
        setAssistantMessage('Professional Interviewer Created Successfully with Enhanced Knowledge Base!');
        setCallForm(prev => ({
          ...prev,
          vapi_assistant_id: response.data.assistant_data.id
        }));
        await loadAssistants();
      } else {
        setAssistantMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      setAssistantMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setAssistantLoading(false);
    }
  };

  // Voice Provider Functions
  const loadElevenLabsVoices = async () => {
    setVoicesLoading(true);
    try {
      const response = await getElevenLabsVoices();
      if (response.data.success) {
        setElevenLabsVoices(response.data.voices);
        console.log('Loaded ElevenLabs voices:', response.data.voices);
      } else {
        console.error('Failed to load ElevenLabs voices:', response.data.error);
      }
    } catch (error) {
      console.error('Error loading ElevenLabs voices:', error);
    } finally {
      setVoicesLoading(false);
    }
  };

  // Effect to load voices when provider changes
  useEffect(() => {
    if (assistantForm.voice_provider === '11labs') {
      loadElevenLabsVoices();
      // Reset to first ElevenLabs voice when switching
      if (elevenLabsVoices.length > 0) {
        setAssistantForm(prev => ({
          ...prev,
          voice_id: elevenLabsVoices[0].voice_id
        }));
      }
    } else {
      // Reset to OpenAI default voice when switching back
      setAssistantForm(prev => ({
        ...prev,
        voice_id: 'nova'
      }));
    }
  }, [assistantForm.voice_provider, elevenLabsVoices.length]);

  // Transcript Functions
  const loadAllCalls = async () => {
    setTranscriptLoading(true);
    try {
      const response = await getCalls(campaignId);
      if (response.data) {
        setAllCalls(response.data);
        console.log('Loaded calls:', response.data);
      }
    } catch (error) {
      console.error('Error loading calls:', error);
    } finally {
      setTranscriptLoading(false);
    }
  };

  const loadCallTranscript = async (callId) => {
    try {
      const response = await getCallDetails(callId);
      if (response.data && response.data.success) {
        setSelectedCall(response.data.call);
      }
    } catch (error) {
      console.error('Error loading call details:', error);
    }
  };

  const formatTranscriptText = (transcript) => {
    if (!transcript) return 'No transcript available';
    
    if (typeof transcript === 'string') {
      return transcript;
    }
    
    if (Array.isArray(transcript)) {
      return transcript.map(item => {
        if (typeof item === 'object' && item.role && item.message) {
          return `${item.role.toUpperCase()}: ${item.message}`;
        }
        return item.toString();
      }).join('\n\n');
    }
    
    return JSON.stringify(transcript, null, 2);
  };

  const getFilteredCalls = () => {
    if (!transcriptSearch.trim()) {
      return allCalls;
    }
    
    return allCalls.filter(call => {
      const searchTerm = transcriptSearch.toLowerCase();
      return (
        call.customer_number?.toLowerCase().includes(searchTerm) ||
        call.status?.toLowerCase().includes(searchTerm) ||
        call.transcript_text?.toLowerCase().includes(searchTerm) ||
        call.assistant?.name?.toLowerCase().includes(searchTerm)
      );
    });
  };

  // Phone Number Functions
  const loadTwilioNumbers = async () => {
    setPhoneLoading(true);
    setPhoneMessage('');
    
    try {
      const response = await getTwilioPhoneNumbers();
      if (response.data.success) {
        setTwilioNumbers(response.data.twilio_numbers);
      } else {
        setPhoneMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      setPhoneMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setPhoneLoading(false);
    }
  };

  const loadVapiNumbers = async () => {
    setPhoneLoading(true);
    setPhoneMessage('');
    
    try {
      const response = await getVapiPhoneNumbers();
      if (response.data.success) {
        setVapiNumbers(response.data.phone_numbers);
        if (response.data.phone_numbers.length > 0) {
          setCallForm(prev => ({
            ...prev,
            twilio_phone_number_id: response.data.phone_numbers[0].id
          }));
        }
      } else {
        setPhoneMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      setPhoneMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setPhoneLoading(false);
    }
  };

  const handleRegisterPhone = async (phoneNumber) => {
    try {
      const response = await registerPhoneNumber(phoneNumber, campaignId);
      if (response.data.success) {
        setPhoneMessage('Number Registered with Vapi successfully!');
        setCallForm(prev => ({
          ...prev,
          twilio_phone_number_id: response.data.vapi_phone_number.id
        }));
        await loadVapiNumbers();
      } else {
        setPhoneMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      setPhoneMessage(`Error: ${error.response?.data?.error || error.message}`);
    }
  };

  // Call Functions
  const handleMakeCall = async (e) => {
    e.preventDefault();
    setCallLoading(true);
    setCallMessage('');

    try {
      console.log('Making call with form data:', callForm);
      
      // Validate required fields
      if (!callForm.customer_number) {
        setCallMessage('Please enter a customer phone number');
        return;
      }
      if (!callForm.vapi_assistant_id) {
        setCallMessage('Please select an assistant first');
        return;
      }

      const response = await makeCall(callForm);
      console.log('Call response:', response);
      
      if (response.data.success) {
        setCurrentCall(response.data.call_data);
        await refreshCallDetails();
        // Refresh transcript data to show the new call
        await loadAllCalls();
        setCallMessage('Call initiated successfully! Check the Transcripts tab for updates.');
      } else {
        setCallMessage(`Error: ${response.data.error || 'Unknown error occurred'}`);
      }
    } catch (error) {
      console.error('Call error:', error);
      console.error('Error response:', error.response?.data);
      setCallMessage(`Error: ${error.response?.data?.error || error.response?.data?.detail || error.message || 'Failed to make call'}`);
    } finally {
      setCallLoading(false);
    }
  };

  const refreshCallDetails = async () => {
    if (!currentCall?.id) return;

    try {
      const response = await getCallDetails(currentCall.id);
      if (response.data.success) {
        setCallDetails(response.data.call);
        setCurrentCall(response.data.call);
      }
    } catch (error) {
      console.error('Error refreshing call details:', error);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'ended': return 'bg-green-100 text-green-800';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800';
      case 'queued': case 'ringing': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getOutcomeColor = (outcome) => {
    switch(outcome) {
      case 'answered': case 'completed': return 'bg-green-100 text-green-800';
      case 'answered-brief': return 'bg-blue-100 text-blue-800';
      case 'voicemail': return 'bg-gray-100 text-gray-800';
      case 'no-answer': case 'busy': case 'declined': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Scheduled Call Functions
  const loadScheduledCalls = async () => {
    try {
      const response = await getScheduledCalls(campaignId);
      setScheduledCalls(response.data);
    } catch (error) {
      console.error('Error loading scheduled calls:', error);
    }
  };

  const handleScheduleCall = async (e) => {
    e.preventDefault();
    setScheduleLoading(true);
    setScheduleMessage('');

    try {
      // Validate required fields
      if (!scheduleForm.customer_number || !scheduleForm.twilio_phone_number_id || 
          !scheduleForm.vapi_assistant_id || !scheduleForm.scheduled_time) {
        setScheduleMessage('Please fill in all required fields');
        setScheduleLoading(false);
        return;
      }

      // Convert local datetime to UTC considering the selected timezone
      const localDateTime = scheduleForm.scheduled_time;
      const selectedTimezone = scheduleForm.timezone;
      
      // Create a date object treating the input as being in the selected timezone
      const scheduledDate = new Date(localDateTime);
      const now = new Date();
      
      console.log('Input datetime-local:', localDateTime);
      console.log('Selected timezone:', selectedTimezone);
      console.log('Parsed date (browser timezone):', scheduledDate);
      console.log('Current time:', now);
      
      if (scheduledDate <= now) {
        setScheduleMessage('Scheduled time must be in the future');
        setScheduleLoading(false);
        return;
      }

      // Convert to UTC for backend storage
      // The datetime-local input gives us a "naive" time that we want to interpret as being in the selected timezone
      
      // Parse the date and time components
      const [datePart, timePart] = localDateTime.split('T');
      const [year, month, day] = datePart.split('-').map(Number);
      const [hours, minutes] = timePart.split(':').map(Number);
      
      // Create a date string that represents the desired time in the selected timezone
      const dateTimeString = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}T${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:00`;
      
      // Use Intl API to properly handle the timezone conversion
      // This creates a date that represents the specified time in the selected timezone
      const dateInSelectedTZ = new Date(dateTimeString);
      
      // Get what this date would be when interpreted in the selected timezone
      const utcOffset = new Date().getTimezoneOffset(); // Browser's timezone offset in minutes
      
      // Proper timezone conversion using a much simpler approach
      // The goal: if user selects 3:30 AM in Asia/Karachi, we need the UTC time that represents 3:30 AM in that timezone
      let utcTime;
      try {
        // Simple and reliable method: manually calculate based on known timezone offset
        const inputDate = new Date(dateTimeString);
        
        // For Asia/Karachi (PKT), which is UTC+5:
        // If user wants 3:30 AM PKT, the UTC time should be 3:30 - 5 = 22:30 UTC (previous day)
        
        // Get timezone offset for the selected timezone at the given date
        // Create a temporary date to find the offset
        const tempUtc = new Date(dateTimeString + 'Z'); // Treat as UTC
        const tempLocal = new Date(tempUtc.toLocaleString('sv-SE', {timeZone: selectedTimezone}));
        const offsetMs = tempUtc.getTime() - tempLocal.getTime();
        
        // Apply the offset to convert from selected timezone to UTC
        utcTime = new Date(inputDate.getTime() + offsetMs);
        
        console.log('=== Timezone Conversion Debug ===');
        console.log('Input time:', localDateTime);
        console.log('Selected timezone:', selectedTimezone);
        console.log('Input as date object:', inputDate.toISOString());
        console.log('Temp UTC date:', tempUtc.toISOString());
        console.log('Temp local date:', tempLocal.toISOString());
        console.log('Calculated offset (ms):', offsetMs);
        console.log('Calculated offset (hours):', offsetMs / (1000 * 60 * 60));
        console.log('Final UTC time:', utcTime.toISOString());
        console.log('Verification - UTC time in selected TZ:', utcTime.toLocaleString('sv-SE', {timeZone: selectedTimezone}));
        
      } catch (error) {
        console.error('Timezone conversion error:', error);
        // Fallback: treat as UTC
        utcTime = new Date(dateTimeString + 'Z');
      }
      
      const scheduleData = {
        ...scheduleForm,
        scheduled_time: utcTime.toISOString(),
        timezone: selectedTimezone
      };
      
      console.log('Original input time:', localDateTime);
      console.log('Selected timezone:', selectedTimezone);
      console.log('Parsed date/time:', {year, month, day, hours, minutes});
      console.log('Date string:', dateTimeString);
      console.log('Final UTC time:', utcTime.toISOString());
      console.log('Sending schedule data:', scheduleData);
      
      const response = await scheduleCall(scheduleData);
      if (response.data.success) {
        setScheduleMessage('Call scheduled successfully!');
        setScheduleForm({
          customer_number: '',
          twilio_phone_number_id: '',
          vapi_assistant_id: '',
          scheduled_time: '',
          call_name: '',
          notes: '',
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        });
        await loadScheduledCalls();
      } else {
        setScheduleMessage(`Error: ${response.data.error}`);
      }
    } catch (error) {
      setScheduleMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setScheduleLoading(false);
    }
  };

  const handleDeleteScheduledCall = async (callId) => {
    if (!confirm('Are you sure you want to delete this scheduled call?')) {
      return;
    }

    try {
      await deleteScheduledCall(callId);
      setScheduleMessage('Scheduled call deleted successfully');
      await loadScheduledCalls();
    } catch (error) {
      setScheduleMessage(`Error: ${error.response?.data?.error || error.message}`);
    }
  };

  // Website Analysis Functions
  const handleAnalyzeWebsite = async () => {
    if (!websiteUrl.trim()) {
      setAnalysisMessage('Please enter a website URL');
      return;
    }

    setAnalysisLoading(true);
    setAnalysisMessage('');
    console.log('Starting website analysis for:', websiteUrl);

    try {
      const response = await analyzeWebsite(websiteUrl);
      console.log('Received response:', response);
      console.log('Response data keys:', Object.keys(response.data));
      
      if (response.data && response.data.success) {
        console.log('Analysis data:', response.data.analysis);
        console.log('Analysis keys:', Object.keys(response.data.analysis));
        
        // Ensure the analysis data has the expected structure
        const analysisData = response.data.analysis;
        const processedAnalysis = {
          summary: analysisData.summary || 'No summary available',
          company_details: {
            name: analysisData.company_details?.name || 'Unknown Company',
            industry: analysisData.company_details?.industry || 'Unknown Industry',
            location: analysisData.company_details?.location || 'Unknown Location'
          },
          article_topics: Array.isArray(analysisData.article_topics) ? analysisData.article_topics : [],
          keywords: Array.isArray(analysisData.keywords) ? analysisData.keywords : []
        };
        
        console.log('Processed analysis:', processedAnalysis);
        setWebsiteAnalysis(processedAnalysis);
        setAnalysisMessage('Website analyzed successfully!');
        
        // Auto-store in AI Knowledge Base (separate from manual knowledge)
        setAiKnowledgeBase({
          summary: processedAnalysis.summary || '',
          topics: processedAnalysis.article_topics || [],
          keywords: processedAnalysis.keywords || []
        });
        
        // Note: Interview Knowledge Base (knowledge_text) is kept separate for additional manual information
      } else {
        console.error('Analysis failed:', response.data?.error || 'Unknown error');
        setAnalysisMessage(`Error: ${response.data?.error || 'Analysis failed'}`);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      console.error('Error details:', error.response?.data);
      setAnalysisMessage(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setAnalysisLoading(false);
    }
  };

  // AI Knowledge Base Management Functions
  const handleRemoveTopic = (topicIndex) => {
    setAiKnowledgeBase(prev => ({
      ...prev,
      topics: prev.topics.filter((_, index) => index !== topicIndex)
    }));
  };

  const handleRemoveKeyword = (keywordIndex) => {
    setAiKnowledgeBase(prev => ({
      ...prev,
      keywords: prev.keywords.filter((_, index) => index !== keywordIndex)
    }));
  };

  const handleAddNewTopic = () => {
    if (newTopic.trim()) {
      setAiKnowledgeBase(prev => ({
        ...prev,
        topics: [...prev.topics, newTopic.trim()]
      }));
      setNewTopic('');
      setShowAddTopicModal(false);
    }
  };

  const handleAddNewKeyword = () => {
    if (newKeyword.trim()) {
      setAiKnowledgeBase(prev => ({
        ...prev,
        keywords: [...prev.keywords, newKeyword.trim()]
      }));
      setNewKeyword('');
      setShowAddKeywordModal(false);
    }
  };

  // Helper function to combine AI Knowledge Base with manual knowledge for the assistant
  const getCombinedKnowledge = () => {
    const aiSummary = aiKnowledgeBase.summary ? `Business Summary: ${aiKnowledgeBase.summary}\n\n` : '';
    const aiTopics = aiKnowledgeBase.topics.length > 0 ? `Article Topics: ${aiKnowledgeBase.topics.join(', ')}\n\n` : '';
    const aiKeywords = aiKnowledgeBase.keywords.length > 0 ? `Keywords: ${aiKnowledgeBase.keywords.join(', ')}\n\n` : '';
    const manualKnowledge = assistantForm.knowledge_text ? `Additional Information: ${assistantForm.knowledge_text}` : '';
    
    return `${aiSummary}${aiTopics}${aiKeywords}${manualKnowledge}`.trim();
  };

  const getScheduleStatusColor = (status) => {
    switch(status) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatScheduledTime = (timeString, displayTimezone = null) => {
    const date = new Date(timeString);
    // If no specific timezone provided, use browser's local time
    const timezone = displayTimezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    return date.toLocaleDateString("en-US", {
      timeZone: timezone,
      year: 'numeric',
      month: 'numeric', 
      day: 'numeric'
    }) + ' ' + date.toLocaleTimeString("en-US", {
      timeZone: timezone,
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  console.log('About to render InterviewDashboard JSX');
  
  try {
    return (
      <div className="container mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Phone className="h-8 w-8" />
          Professional Interview Assistant
        </h1>
        <p className="text-muted-foreground">
          AI-powered interview system with custom knowledge base and professional voice
        </p>
        {currentCampaign && (
          <div className="mt-4">
            <Badge variant="outline" className="text-lg px-4 py-2">
              Campaign: {currentCampaign.name}
            </Badge>
            {currentCampaign.description && (
              <p className="text-sm text-muted-foreground mt-2">
                {currentCampaign.description}
              </p>
            )}
          </div>
        )}
      </div>

      <Tabs defaultValue="config" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 md:grid-cols-4 lg:grid-cols-7">
          <TabsTrigger value="config" className="flex items-center gap-2 text-sm">
            <Settings className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">Configuration</span>
          </TabsTrigger>
          <TabsTrigger value="prompts" className="flex items-center gap-2 text-sm">
            <FileText className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">Prompts</span>
          </TabsTrigger>
          <TabsTrigger value="assistant" className="flex items-center gap-2 text-sm">
            <User className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">Assistant</span>
          </TabsTrigger>
          <TabsTrigger value="phones" className="flex items-center gap-2 text-sm">
            <Phone className="h-4 w-4 flex-shrink-0" />
            <span className="truncate hidden sm:inline">Phone Numbers</span>
            <span className="truncate sm:hidden">Phones</span>
          </TabsTrigger>
          <TabsTrigger value="calls" className="flex items-center gap-2 text-sm">
            <Shield className="h-4 w-4 flex-shrink-0" />
            <span className="truncate hidden sm:inline">Make Calls</span>
            <span className="truncate sm:hidden">Calls</span>
          </TabsTrigger>
          <TabsTrigger value="scheduled" className="flex items-center gap-2 text-sm">
            <Calendar className="h-4 w-4 flex-shrink-0" />
            <span className="truncate hidden sm:inline">Schedule Calls</span>
            <span className="truncate sm:hidden">Schedule</span>
          </TabsTrigger>
          <TabsTrigger value="transcripts" className="flex items-center gap-2 text-sm">
            <FileText className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">Transcripts</span>
          </TabsTrigger>
        </TabsList>

        {/* API Configuration Tab */}
        <TabsContent value="config">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                API Configuration
              </CardTitle>
              <CardDescription>
                Configure your Twilio, Vapi, and OpenAI API credentials
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <span>Twilio Configured:</span>
                  {apiConfig.is_twilio_configured ? (
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" /> Yes
                    </Badge>
                  ) : (
                    <Badge variant="destructive">
                      <XCircle className="h-3 w-3 mr-1" /> No
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span>Vapi Configured:</span>
                  {apiConfig.is_vapi_configured ? (
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" /> Yes
                    </Badge>
                  ) : (
                    <Badge variant="destructive">
                      <XCircle className="h-3 w-3 mr-1" /> No
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span>OpenAI Configured:</span>
                  {apiConfig.is_openai_configured ? (
                    <Badge className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" /> Yes
                    </Badge>
                  ) : (
                    <Badge variant="destructive">
                      <XCircle className="h-3 w-3 mr-1" /> No
                    </Badge>
                  )}
                </div>
              </div>

              <form onSubmit={handleConfigSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="twilioAccountSid">Twilio Account SID</Label>
                  <Input
                    id="twilioAccountSid"
                    value={apiConfig.twilio_account_sid}
                    onChange={(e) => setApiConfig(prev => ({
                      ...prev,
                      twilio_account_sid: e.target.value
                    }))}
                    placeholder="Enter Twilio Account SID"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="twilioAuthToken">Twilio Auth Token</Label>
                  <Input
                    id="twilioAuthToken"
                    type="password"
                    value={apiConfig.twilio_auth_token}
                    onChange={(e) => setApiConfig(prev => ({
                      ...prev,
                      twilio_auth_token: e.target.value
                    }))}
                    placeholder="Enter Twilio Auth Token"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="vapiApiKey">Vapi API Key</Label>
                  <Input
                    id="vapiApiKey"
                    type="password"
                    value={apiConfig.vapi_api_key}
                    onChange={(e) => setApiConfig(prev => ({
                      ...prev,
                      vapi_api_key: e.target.value
                    }))}
                    placeholder="Enter Vapi API Key"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="openaiApiKey">OpenAI API Key</Label>
                  <Input
                    id="openaiApiKey"
                    type="password"
                    value={apiConfig.openai_api_key}
                    onChange={(e) => setApiConfig(prev => ({
                      ...prev,
                      openai_api_key: e.target.value
                    }))}
                    placeholder="Enter OpenAI API Key (starts with sk-)"
                  />
                </div>

                <div className="flex gap-2">
                  <Button type="submit" disabled={configLoading}>
                    {configLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Save Configuration
                  </Button>
                  <Button type="button" variant="outline" onClick={handleClearConfig}>
                    Clear Configuration
                  </Button>
                </div>
              </form>

              {configMessage && (
                <Alert className={configMessage.includes('Error') ? 'border-red-200' : 'border-green-200'}>
                  <AlertDescription>{configMessage}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Prompts Configuration Tab */}
        <TabsContent value="prompts">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                VAPI Prompt Configuration
              </CardTitle>
              <CardDescription>
                Configure the AI system prompts and messages for your interview assistant
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              
              {/* System Prompt */}
              <div className="space-y-2">
                <Label htmlFor="systemPrompt">System Prompt</Label>
                <Textarea
                  id="systemPrompt"
                  value={promptForm.system_prompt}
                  onChange={(e) => setPromptForm(prev => ({
                    ...prev,
                    system_prompt: e.target.value
                  }))}
                  placeholder="Enter the main system prompt that defines the AI interviewer's behavior..."
                  rows={12}
                  className="font-mono text-sm"
                />
                <p className="text-sm text-muted-foreground">
                  This is the main system prompt that defines how the AI interviewer behaves during voice calls.
                </p>
              </div>

              {/* First Message */}
              <div className="space-y-2">
                <Label htmlFor="firstMessage">First Message</Label>
                <Input
                  id="firstMessage"
                  value={promptForm.first_message}
                  onChange={(e) => setPromptForm(prev => ({
                    ...prev,
                    first_message: e.target.value
                  }))}
                  placeholder="Good day, I'll be conducting your interview today. Let's begin."
                />
                <p className="text-sm text-muted-foreground">
                  The opening message the AI will say when the call starts.
                </p>
              </div>

              {/* End Call Phrases */}
              <div className="space-y-2">
                <Label htmlFor="endCallPhrases">End Call Trigger Phrases</Label>
                <Textarea
                  id="endCallPhrases"
                  value={promptForm.end_call_phrases}
                  onChange={(e) => setPromptForm(prev => ({
                    ...prev,
                    end_call_phrases: e.target.value
                  }))}
                  placeholder="Enter phrases that should trigger the end of the call, one per line..."
                  rows={5}
                />
                <p className="text-sm text-muted-foreground">
                  Phrases that will automatically end the call when detected (one per line).
                </p>
              </div>

              {/* Prompt Template Buttons */}
              <div className="space-y-3">
                <Label>Quick Templates</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setPromptForm(prev => ({
                      ...prev,
                      system_prompt: `🎤 YOU ARE ON A LIVE TECHNICAL VOICE CALL INTERVIEW 🎤
You are conducting a REAL-TIME PHONE CONVERSATION with a technical candidate. This is NOT text messaging or chat.

📞 VOICE CALL REQUIREMENTS:
- SPEAK naturally as if talking on the phone about technical topics
- Use verbal communication style (not written text style)
- Keep technical explanations conversational and engaging for voice
- Use phone etiquette throughout the technical interview
- Remember: the candidate can HEAR you discussing technical concepts

🔧 TECHNICAL SKILLS FOCUS:
- Programming languages and frameworks
- Problem-solving approach
- System design thinking
- Code quality and best practices

📰 STRICT SEQUENTIAL TECHNICAL ARTICLE PROCESSING:
You MUST process technical articles in this EXACT order:

🔒 **CRITICAL RULE: ONE TECHNICAL ARTICLE AT A TIME**
- Start with Technical Article 1 ONLY
- Do NOT mention or reference any other technical articles until Article 1 is COMPLETELY finished
- Only move to Technical Article 2 after Article 1 discussion is 100% complete
- Continue this pattern for ALL technical articles in sequence

📋 **TECHNICAL ARTICLE COMPLETION PROCESS:**
For EACH technical article, follow these steps IN ORDER:

1. **Introduce Current Technical Article**: "Let's discuss this technical article about..." 
2. **Explore Technical Concepts**: Thoroughly discuss the technical topics in the article
3. **Assess Technical Understanding**: Ask follow-up questions about technical concepts
4. **Complete Technical Discussion**: Ensure you have thoroughly covered all technical aspects
5. **Move to Next Technical Article**: ONLY then proceed to the next numbered technical article

📝 **TECHNICAL DISCUSSION FOCUS:**
- Ask about the candidate's understanding of technical concepts in the article
- Explore their practical experience with the technologies mentioned
- Assess their problem-solving approach related to the article's topics
- Gather detailed technical responses and insights
- Keep technical discussion focused on the current article only

⚠️ IMPORTANT: You are speaking to a technical candidate on the phone RIGHT NOW. Act accordingly and stay focused on completing one technical article at a time.`
                    }))}
                  >
                    Technical Interview
                  </Button>
                  
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setPromptForm(prev => ({
                      ...prev,
                      system_prompt: `You are an HR interviewer conducting a behavioral interview over the phone. Focus on:

🤝 BEHAVIORAL ASSESSMENT:
- Past experiences and achievements
- Leadership and teamwork skills
- Problem-solving in challenging situations
- Cultural fit and values alignment

📞 VOICE INTERVIEW APPROACH:
- Create a comfortable, conversational atmosphere
- Use STAR method for behavioral questions
- Listen actively and ask follow-up questions
- Maintain professional but warm tone

Evaluate soft skills, motivation, and cultural alignment through engaging conversation.`
                    }))}
                  >
                    Behavioral Interview
                  </Button>
                  
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setPromptForm(prev => ({
                      ...prev,
                      system_prompt: `You are conducting a sales role interview via phone call. Focus on:

💼 SALES ASSESSMENT:
- Sales experience and methodology
- Communication and persuasion skills
- Customer relationship management
- Results and performance metrics

📞 SALES INTERVIEW STYLE:
- Engage in dynamic, energetic conversation
- Test communication skills in real-time
- Evaluate confidence and presentation ability
- Assess consultative selling approach

Maintain high energy and evaluate both sales acumen and phone presence.`
                    }))}
                  >
                    Sales Interview
                  </Button>
                </div>
              </div>

              {/* Save Button */}
              <div className="pt-4">
                <Button 
                  onClick={() => {
                    // Save prompts (could add API call here)
                    alert('Prompts saved! These will be used when creating new assistants.');
                  }}
                  className="w-full"
                >
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Save Prompt Configuration
                </Button>
              </div>

            </CardContent>
          </Card>
        </TabsContent>

        {/* Assistant Configuration Tab */}
        <TabsContent value="assistant">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Configure Interview Assistant
              </CardTitle>
              <CardDescription>
                Create and configure your AI interviewer
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handleAssistantSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="assistantName">Interviewer Name</Label>
                    <Input
                      id="assistantName"
                      value={assistantForm.name}
                      onChange={(e) => setAssistantForm(prev => ({
                        ...prev,
                        name: e.target.value
                      }))}
                      placeholder="Professional Interviewer"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="firstMessage">Opening Statement</Label>
                    <Input
                      id="firstMessage"
                      value={assistantForm.first_message}
                      readOnly
                      placeholder="Controlled by Prompts tab"
                      className="bg-gray-50"
                    />
                    <p className="text-sm text-muted-foreground">
                      This is controlled by the <strong>Prompts</strong> tab. Go to the Prompts tab to edit the first message.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="voiceProvider">Voice Provider</Label>
                    <select
                      id="voiceProvider"
                      className="w-full p-2 border rounded"
                      value={assistantForm.voice_provider}
                      onChange={(e) => setAssistantForm(prev => ({
                        ...prev,
                        voice_provider: e.target.value
                      }))}
                    >
                      <option value="openai">OpenAI (Recommended)</option>
                      <option value="11labs">ElevenLabs</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="voiceId">Voice Selection</Label>
                    <select
                      id="voiceId"
                      className="w-full p-2 border rounded"
                      value={assistantForm.voice_id}
                      onChange={(e) => setAssistantForm(prev => ({
                        ...prev,
                        voice_id: e.target.value
                      }))}
                      disabled={voicesLoading}
                    >
                      {assistantForm.voice_provider === '11labs' ? (
                        // ElevenLabs voices
                        voicesLoading ? (
                          <option value="">Loading voices...</option>
                        ) : elevenLabsVoices.length > 0 ? (
                          elevenLabsVoices.map((voice) => (
                            <option key={voice.voice_id} value={voice.voice_id}>
                              {voice.name} ({voice.description})
                            </option>
                          ))
                        ) : (
                          <option value="">No voices available</option>
                        )
                      ) : (
                        // OpenAI voices (default)
                        <>
                          <option value="nova">Nova (Professional Female)</option>
                          <option value="onyx">Onyx (Professional Male)</option>
                          <option value="alloy">Alloy (Neutral)</option>
                          <option value="echo">Echo (Clear)</option>
                          <option value="fable">Fable (Warm)</option>
                          <option value="shimmer">Shimmer (Gentle)</option>
                        </>
                      )}
                    </select>
                    {voicesLoading && (
                      <div className="text-sm text-gray-500 flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Loading ElevenLabs voices...
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="modelProvider">AI Model Provider</Label>
                    <select
                      id="modelProvider"
                      className="w-full p-2 border rounded"
                      value={assistantForm.model_provider}
                      onChange={(e) => setAssistantForm(prev => ({
                        ...prev,
                        model_provider: e.target.value
                      }))}
                    >
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="model">AI Model</Label>
                    <select
                      id="model"
                      className="w-full p-2 border rounded"
                      value={assistantForm.model}
                      onChange={(e) => setAssistantForm(prev => ({
                        ...prev,
                        model: e.target.value
                      }))}
                    >
                      {assistantForm.model_provider === 'anthropic' ? (
                        <>
                          <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Latest)</option>
                          <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                          <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                        </>
                      ) : (
                        // OpenAI models (default)
                        <>
                          <option value="gpt-4">GPT-4 (Current)</option>
                          <option value="gpt-4-turbo">GPT-4 Turbo</option>
                          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                        </>
                      )}
                    </select>
                    <p className="text-sm text-gray-600">
                      Currently using: <strong>{assistantForm.model_provider} - {assistantForm.model}</strong>
                    </p>
                  </div>
                </div>

                {/* Website Analysis Section */}
                <div className="border rounded-lg p-6 space-y-6 bg-white shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                      <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Website Analysis</h3>
                      <p className="text-sm text-gray-600">Enter a website URL to automatically extract business insights</p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <div className="flex-1">
                      <Input
                        placeholder="https://example.com"
                        value={websiteUrl}
                        onChange={(e) => setWebsiteUrl(e.target.value)}
                        className="h-11 border-gray-300 focus:border-blue-500"
                      />
                    </div>
                    <Button 
                      type="button"
                      onClick={handleAnalyzeWebsite}
                      disabled={analysisLoading}
                      className="h-11 px-6 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white"
                    >
                      {analysisLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      {analysisLoading ? 'Analyzing...' : 'Analyze Website'}
                    </Button>
                  </div>

                  {analysisMessage && (
                    <Alert className={analysisMessage.includes('Error') ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'}>
                      <AlertDescription className={analysisMessage.includes('Error') ? 'text-red-800' : 'text-green-800'}>
                        {analysisMessage}
                      </AlertDescription>
                    </Alert>
                  )}

                  {websiteAnalysis && (
                    <div className="space-y-6 border-t border-gray-200 pt-6">
                      {/* Header with sync info */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-sm text-blue-600">
                          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Analysis Complete
                        </div>
                        <span className="text-xs text-gray-500">Just now</span>
                      </div>

                      {/* Company Information Card */}
                      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                              <svg className="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H3m2 0h3M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                              </svg>
                            </div>
                            <h4 className="font-semibold text-gray-900">Business Information</h4>
                          </div>
                          <Button variant="outline" size="sm" className="text-blue-600 border-blue-200 hover:bg-blue-50">
                            Edit
                          </Button>
                        </div>
                        
                        <div className="space-y-3">
                          {websiteAnalysis.company_details?.name && (
                            <div>
                              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Company Name</label>
                              <div className="mt-1 text-sm font-medium text-gray-900">{websiteAnalysis.company_details.name}</div>
                            </div>
                          )}
                          
                          {websiteAnalysis.company_details?.industry && (
                            <div>
                              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Industry</label>
                              <div className="mt-1 text-sm text-gray-700">{websiteAnalysis.company_details.industry}</div>
                            </div>
                          )}
                          
                          {websiteAnalysis.summary && (
                            <div>
                              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Business Summary</label>
                              <div className="mt-1 text-sm text-gray-700 leading-relaxed">{websiteAnalysis.summary}</div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Article Topics Section */}
                      {(aiKnowledgeBase.topics.length > 0 || websiteAnalysis?.article_topics?.length > 0) && (
                        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                              <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                                <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                              </div>
                              <h4 className="font-semibold text-gray-900">Article Topics</h4>
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                                {aiKnowledgeBase.topics.length} topics
                              </span>
                            </div>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="text-green-600 border-green-200 hover:bg-green-50"
                              onClick={() => setShowAddTopicModal(true)}
                            >
                              ➕ Add Topic
                            </Button>
                          </div>
                          
                          <div className="flex flex-wrap gap-2">
                            {aiKnowledgeBase.topics.map((topic, index) => (
                              <div key={index} className="relative group">
                                <Badge 
                                  variant="secondary" 
                                  className="bg-white border border-gray-300 text-gray-700 hover:bg-green-50 hover:border-green-300 transition-colors pr-8"
                                >
                                  {topic}
                                  <button
                                    onClick={() => handleRemoveTopic(index)}
                                    className="absolute right-1 top-1/2 transform -translate-y-1/2 text-red-500 hover:text-red-700 text-xs"
                                  >
                                    ✕
                                  </button>
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Keywords Section */}
                      {(aiKnowledgeBase.keywords.length > 0 || websiteAnalysis?.keywords?.length > 0) && (
                        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                              <div className="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                <svg className="h-4 w-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                                </svg>
                              </div>
                              <h4 className="font-semibold text-gray-900">Keywords</h4>
                              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                                {aiKnowledgeBase.keywords.length} keywords
                              </span>
                            </div>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="text-purple-600 border-purple-200 hover:bg-purple-50"
                              onClick={() => setShowAddKeywordModal(true)}
                            >
                              ➕ Add Keyword
                            </Button>
                          </div>
                          
                          <div className="flex flex-wrap gap-2">
                            {aiKnowledgeBase.keywords.map((keyword, index) => (
                              <div key={index} className="relative group">
                                <Badge 
                                  variant="outline" 
                                  className="bg-white border border-gray-300 text-gray-700 hover:bg-purple-50 hover:border-purple-300 transition-colors pr-8"
                                >
                                  {keyword}
                                  <button
                                    onClick={() => handleRemoveKeyword(index)}
                                    className="absolute right-1 top-1/2 transform -translate-y-1/2 text-red-500 hover:text-red-700 text-xs"
                                  >
                                    ✕
                                  </button>
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Add Topic Modal */}
                {showAddTopicModal && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-96 max-w-90vw">
                      <h3 className="text-lg font-semibold mb-4">Add New Article Topic</h3>
                      <input
                        type="text"
                        value={newTopic}
                        onChange={(e) => setNewTopic(e.target.value)}
                        placeholder="Enter article topic..."
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleAddNewTopic()}
                      />
                      <div className="flex gap-3 mt-4">
                        <Button 
                          onClick={handleAddNewTopic}
                          className="flex-1 bg-green-600 hover:bg-green-700"
                        >
                          Add Topic
                        </Button>
                        <Button 
                          variant="outline" 
                          onClick={() => {setShowAddTopicModal(false); setNewTopic('');}}
                          className="flex-1"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Add Keyword Modal */}
                {showAddKeywordModal && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 w-96 max-w-90vw">
                      <h3 className="text-lg font-semibold mb-4">Add New Keyword</h3>
                      <input
                        type="text"
                        value={newKeyword}
                        onChange={(e) => setNewKeyword(e.target.value)}
                        placeholder="Enter keyword..."
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleAddNewKeyword()}
                      />
                      <div className="flex gap-3 mt-4">
                        <Button 
                          onClick={handleAddNewKeyword}
                          className="flex-1 bg-purple-600 hover:bg-purple-700"
                        >
                          Add Keyword
                        </Button>
                        <Button 
                          variant="outline" 
                          onClick={() => {setShowAddKeywordModal(false); setNewKeyword('');}}
                          className="flex-1"
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="knowledgeText">Additional Interview Knowledge (Manual Input)</Label>
                  <p className="text-sm text-gray-600">Add extra information beyond the website analysis that you want the AI agent to know about.</p>
                  <Textarea
                    id="knowledgeText"
                    rows={6}
                    value={assistantForm.knowledge_text}
                    onChange={(e) => setAssistantForm(prev => ({
                      ...prev,
                      knowledge_text: e.target.value
                    }))}
                    placeholder="Enter additional interview topics, specific role requirements, company culture details, or any other information you want the AI agent to know about..."
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="knowledgeUrls">Reference URLs (one per line)</Label>
                  <Textarea
                    id="knowledgeUrls"
                    rows={4}
                    value={assistantForm.knowledge_urls}
                    onChange={(e) => setAssistantForm(prev => ({
                      ...prev,
                      knowledge_urls: e.target.value
                    }))}
                    placeholder="https://company.com/about&#10;https://company.com/careers&#10;https://docs.company.com/role-description"
                  />
                  <p className="text-sm text-muted-foreground">
                    Add URLs for additional context (company website, job descriptions, etc.)
                  </p>
                </div>

                <Button type="submit" disabled={assistantLoading} className="w-full">
                  {assistantLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  🚀 Create Professional Interviewer
                </Button>
              </form>

              {assistantMessage && (
                <Alert className={assistantMessage.includes('Error') ? 'border-red-200' : 'border-green-200'}>
                  <AlertDescription>{assistantMessage}</AlertDescription>
                </Alert>
              )}

              {/* Display existing assistants */}
              {assistants.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-semibold">Your Assistants</h3>
                  <div className="space-y-2">
                    {assistants.map((assistant) => (
                      <div key={assistant.id} className="p-3 border rounded">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium">{assistant.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              Voice: {assistant.voice_id} ({assistant.voice_provider})
                            </p>
                            <p className="text-xs text-muted-foreground">
                              ID: {assistant.vapi_assistant_id}
                            </p>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => {
                              setCallForm(prev => ({
                                ...prev,
                                vapi_assistant_id: assistant.vapi_assistant_id
                              }));
                              setCallMessage(`✅ Assistant "${assistant.name}" is now selected for calls!`);
                              setTimeout(() => setCallMessage(''), 3000);
                            }}
                          >
                            Use for Calls
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Phone Numbers Tab */}
        <TabsContent value="phones">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Phone className="h-5 w-5" />
                Phone Number Management
              </CardTitle>
              <CardDescription>
                Manage your Twilio phone numbers and register them with Vapi
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Button 
                  onClick={loadVapiNumbers}
                  disabled={phoneLoading}
                  variant="outline"
                >
                  {phoneLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  List Vapi Phone Numbers
                </Button>
                <Button 
                  onClick={loadTwilioNumbers}
                  disabled={phoneLoading}
                >
                  {phoneLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Show My Twilio Numbers
                </Button>
              </div>

              {phoneMessage && (
                <Alert className={phoneMessage.includes('Error') ? 'border-red-200' : 'border-green-200'}>
                  <AlertDescription>{phoneMessage}</AlertDescription>
                </Alert>
              )}

              {/* Vapi Numbers */}
              {vapiNumbers.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-semibold">Available Vapi Phone Numbers</h3>
                  <div className="space-y-2">
                    {vapiNumbers.map((number) => (
                      <div key={number.id} className="p-3 border rounded">
                        <p><strong>ID:</strong> {number.id}</p>
                        <p><strong>Number:</strong> {number.number}</p>
                        <Button
                          size="sm"
                          className="mt-2"
                          onClick={() => {
                            setCallForm(prev => ({
                              ...prev,
                              twilio_phone_number_id: number.id
                            }));
                            setCallMessage(`✅ Phone number "${number.number}" is now selected for calls!`);
                            setTimeout(() => setCallMessage(''), 3000);
                          }}
                        >
                          Use for Calls
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Twilio Numbers */}
              {twilioNumbers.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-semibold">Your Twilio Numbers</h3>
                  <div className="space-y-2">
                    {twilioNumbers.map((number) => (
                      <div key={number.sid} className="p-3 border rounded">
                        <p><strong>Number:</strong> {number.phone_number}</p>
                        <p><strong>Name:</strong> {number.friendly_name}</p>
                        <p><strong>Capabilities:</strong> {
                          Object.entries(number.capabilities)
                            .filter(([key, value]) => value)
                            .map(([key]) => key.toUpperCase())
                            .join(', ')
                        }</p>
                        <Button
                          size="sm"
                          className="mt-2"
                          onClick={() => handleRegisterPhone(number.phone_number)}
                        >
                          Register with Vapi
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Make Calls Tab */}
        <TabsContent value="calls">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  Start Interview Call
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleMakeCall} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="customerNumber">Interviewee Phone Number</Label>
                    <Input
                      id="customerNumber"
                      type="tel"
                      value={callForm.customer_number}
                      onChange={(e) => setCallForm(prev => ({
                        ...prev,
                        customer_number: e.target.value
                      }))}
                      placeholder="+1-555-123-4567"
                      required
                    />
                    <p className="text-sm text-muted-foreground">
                      Enter the candidate's phone number for the interview
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="twilioPhoneNumberId">Your Phone Number (Vapi ID)</Label>
                    <Input
                      id="twilioPhoneNumberId"
                      value={callForm.twilio_phone_number_id}
                      onChange={(e) => setCallForm(prev => ({
                        ...prev,
                        twilio_phone_number_id: e.target.value
                      }))}
                      placeholder="Auto-filled from registration"
                      readOnly
                      className="bg-gray-50"
                    />
                    <p className="text-sm text-muted-foreground">
                      Automatically filled after registering your Twilio number
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="vapiAssistantId">Interview Assistant ID</Label>
                    <Input
                      id="vapiAssistantId"
                      value={callForm.vapi_assistant_id}
                      onChange={(e) => setCallForm(prev => ({
                        ...prev,
                        vapi_assistant_id: e.target.value
                      }))}
                      placeholder="Auto-filled from assistant creation"
                      readOnly
                      className="bg-gray-50"
                    />
                    <p className="text-sm text-muted-foreground">
                      Automatically filled after creating your interviewer
                    </p>
                  </div>

                  <Button type="submit" disabled={callLoading} className="w-full">
                    {callLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    🚀 Begin Professional Interview
                  </Button>
                </form>

                {/* Call Form Messages */}
                {callMessage && (
                  <Alert className="mt-4">
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>{callMessage}</AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Call Status */}
            {currentCall && (
              <Card>
                <CardHeader>
                  <CardTitle>Call Status & Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span>Status:</span>
                      <Badge className={getStatusColor(currentCall.status || 'unknown')}>
                        {(currentCall.status || 'Unknown').toUpperCase()}
                      </Badge>
                    </div>

                    {callDetails?.outcome && (
                      <div className="flex items-center gap-2">
                        <span>Outcome:</span>
                        <Badge className={getOutcomeColor(callDetails.outcome.status)}>
                          {callDetails.outcome.status.toUpperCase()}
                        </Badge>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    {/* Call Information Section */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-3">Call Information</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <label className="font-medium text-gray-600">Phone Number:</label>
                          <p className="mt-1">{currentCall?.customer_number || currentCall?.customer?.number || callDetails?.customer_number || callDetails?.customer?.number || callForm?.customer_number || 'N/A'}</p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">Status:</label>
                          <p className="mt-1">
                            <Badge className={getStatusColor(currentCall?.status || callDetails?.status || 'unknown')}>
                              {(currentCall?.status || callDetails?.status || 'Unknown').toUpperCase()}
                            </Badge>
                          </p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">Assistant:</label>
                          <p className="mt-1">{callDetails?.assistant?.name || currentCall?.assistant?.name || (callForm?.vapi_assistant_id && assistants.find(a => a.vapi_assistant_id === callForm.vapi_assistant_id)?.name) || 'N/A'}</p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">Campaign:</label>
                          <p className="mt-1">{currentCampaign?.name || 'N/A'}</p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">Duration:</label>
                          <p className="mt-1">{callDetails?.duration_formatted || (callDetails?.duration_seconds ? `${Math.floor(callDetails.duration_seconds / 60)}m ${callDetails.duration_seconds % 60}s` : 'N/A')}</p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">Cost:</label>
                          <p className="mt-1">${callDetails?.cost ? callDetails.cost.toFixed(4) : '0.00'}</p>
                        </div>
                      </div>
                    </div>

                    {/* Timeline Section */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-3">Timeline</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <label className="font-medium text-gray-600">Created:</label>
                          <p className="mt-1">{callDetails?.created_at ? new Date(callDetails.created_at).toLocaleString() : currentCall?.created_at ? new Date(currentCall.created_at).toLocaleString() : 'N/A'}</p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">Started:</label>
                          <p className="mt-1">{callDetails?.started_at ? new Date(callDetails.started_at).toLocaleString() : 'N/A'}</p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">Ended:</label>
                          <p className="mt-1">{callDetails?.ended_at ? new Date(callDetails.ended_at).toLocaleString() : 'N/A'}</p>
                        </div>
                        <div>
                          <label className="font-medium text-gray-600">End Reason:</label>
                          <p className="mt-1">{callDetails?.outcome?.description || callDetails?.end_reason || 'N/A'}</p>
                        </div>
                      </div>
                    </div>

                    {/* Additional Details */}
                    {callDetails && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-semibold text-gray-900 mb-3">Additional Details</h4>
                        <div className="space-y-2 text-sm">
                          <p><strong>Call ID:</strong> {callDetails.id || currentCall?.id || 'N/A'}</p>
                          <p><strong>VAPI Call ID:</strong> {callDetails.vapi_call_id || currentCall?.vapi_call_id || 'N/A'}</p>
                          {callDetails.outcome && (
                            <p><strong>Outcome Status:</strong> 
                              <Badge className={getOutcomeColor(callDetails.outcome.status)} style={{marginLeft: '8px'}}>
                                {callDetails.outcome.status.toUpperCase()}
                              </Badge>
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {callDetails?.transcript_text && (
                    <div className="space-y-2">
                      <h4 className="font-semibold">Call Transcript</h4>
                      <div className="p-3 bg-gray-50 rounded max-h-64 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-xs">
                          {callDetails.transcript_text}
                        </pre>
                      </div>
                    </div>
                  )}

                  <Button 
                    variant="outline" 
                    onClick={refreshCallDetails}
                    className="w-full"
                  >
                    Refresh Call Details
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Scheduled Calls Tab */}
        <TabsContent value="scheduled">
          <div className="grid gap-6">
            {/* Schedule New Call Form */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Schedule New Call
                </CardTitle>
                <CardDescription>
                  Schedule interview calls to be made automatically at specific times
                </CardDescription>
              </CardHeader>
              <CardContent>
                {scheduleMessage && (
                  <Alert className="mb-4">
                    <AlertDescription>{scheduleMessage}</AlertDescription>
                  </Alert>
                )}

                <form onSubmit={handleScheduleCall} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="schedule-customer-number">Customer Phone Number *</Label>
                      <Input
                        id="schedule-customer-number"
                        type="tel"
                        placeholder="+1234567890"
                        value={scheduleForm.customer_number}
                        onChange={(e) => setScheduleForm(prev => ({
                          ...prev,
                          customer_number: e.target.value
                        }))}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="schedule-call-name">Call Name (Optional)</Label>
                      <Input
                        id="schedule-call-name"
                        placeholder="Interview for John Doe"
                        value={scheduleForm.call_name}
                        onChange={(e) => setScheduleForm(prev => ({
                          ...prev,
                          call_name: e.target.value
                        }))}
                      />
                    </div>

                    <div>
                      <Label htmlFor="schedule-phone-number">Your Phone Number *</Label>
                      <select
                        id="schedule-phone-number"
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                        value={scheduleForm.twilio_phone_number_id}
                        onChange={(e) => setScheduleForm(prev => ({
                          ...prev,
                          twilio_phone_number_id: e.target.value
                        }))}
                        required
                      >
                        <option value="">Select a phone number</option>
                        {vapiNumbers.map((number) => (
                          <option key={number.id} value={number.id}>
                            {number.number} - {number.name || 'Unnamed'}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <Label htmlFor="schedule-assistant">Interview Assistant *</Label>
                      <select
                        id="schedule-assistant"
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                        value={scheduleForm.vapi_assistant_id}
                        onChange={(e) => setScheduleForm(prev => ({
                          ...prev,
                          vapi_assistant_id: e.target.value
                        }))}
                        required
                      >
                        <option value="">Select an assistant</option>
                        {assistants.map((assistant) => (
                          <option key={assistant.id} value={assistant.vapi_assistant_id}>
                            {assistant.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <Label htmlFor="scheduled-time">Scheduled Date & Time *</Label>
                      <Input
                        id="scheduled-time"
                        type="datetime-local"
                        value={scheduleForm.scheduled_time}
                        onChange={(e) => setScheduleForm(prev => ({
                          ...prev,
                          scheduled_time: e.target.value
                        }))}
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="timezone">Your Timezone *</Label>
                      <select
                        id="timezone"
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                        value={scheduleForm.timezone}
                        onChange={(e) => setScheduleForm(prev => ({
                          ...prev,
                          timezone: e.target.value
                        }))}
                        required
                      >
                        <optgroup label="Common Timezones">
                          <option value="America/New_York">Eastern Time (New York)</option>
                          <option value="America/Chicago">Central Time (Chicago)</option>
                          <option value="America/Denver">Mountain Time (Denver)</option>
                          <option value="America/Los_Angeles">Pacific Time (Los Angeles)</option>
                          <option value="Europe/London">GMT (London)</option>
                          <option value="Europe/Paris">CET (Paris)</option>
                          <option value="Asia/Dubai">GST (Dubai)</option>
                          <option value="Asia/Karachi">PKT (Karachi)</option>
                          <option value="Asia/Kolkata">IST (India)</option>
                          <option value="Asia/Shanghai">CST (China)</option>
                          <option value="Asia/Tokyo">JST (Tokyo)</option>
                          <option value="Australia/Sydney">AEST (Sydney)</option>
                        </optgroup>
                        <optgroup label="All Timezones">
                          <option value="UTC">UTC</option>
                          <option value="America/Adak">America/Adak</option>
                          <option value="America/Anchorage">America/Anchorage</option>
                          <option value="America/Anguilla">America/Anguilla</option>
                          <option value="America/Antigua">America/Antigua</option>
                          <option value="America/Araguaina">America/Araguaina</option>
                          <option value="America/Argentina/Buenos_Aires">America/Argentina/Buenos_Aires</option>
                          <option value="America/Aruba">America/Aruba</option>
                          <option value="America/Asuncion">America/Asuncion</option>
                          <option value="America/Atikokan">America/Atikokan</option>
                          <option value="America/Bahia">America/Bahia</option>
                          <option value="America/Bahia_Banderas">America/Bahia_Banderas</option>
                          <option value="America/Barbados">America/Barbados</option>
                          <option value="America/Belem">America/Belem</option>
                          <option value="America/Belize">America/Belize</option>
                          <option value="America/Blanc-Sablon">America/Blanc-Sablon</option>
                          <option value="America/Boa_Vista">America/Boa_Vista</option>
                          <option value="America/Bogota">America/Bogota</option>
                          <option value="America/Boise">America/Boise</option>
                          <option value="America/Cambridge_Bay">America/Cambridge_Bay</option>
                          <option value="America/Campo_Grande">America/Campo_Grande</option>
                          <option value="America/Cancun">America/Cancun</option>
                          <option value="America/Caracas">America/Caracas</option>
                          <option value="America/Cayenne">America/Cayenne</option>
                          <option value="America/Cayman">America/Cayman</option>
                          <option value="America/Chicago">America/Chicago</option>
                          <option value="America/Chihuahua">America/Chihuahua</option>
                          <option value="America/Costa_Rica">America/Costa_Rica</option>
                          <option value="America/Creston">America/Creston</option>
                          <option value="America/Cuiaba">America/Cuiaba</option>
                          <option value="America/Curacao">America/Curacao</option>
                          <option value="America/Danmarkshavn">America/Danmarkshavn</option>
                          <option value="America/Dawson">America/Dawson</option>
                          <option value="America/Dawson_Creek">America/Dawson_Creek</option>
                          <option value="America/Denver">America/Denver</option>
                          <option value="America/Detroit">America/Detroit</option>
                          <option value="America/Dominica">America/Dominica</option>
                          <option value="America/Edmonton">America/Edmonton</option>
                          <option value="America/Eirunepe">America/Eirunepe</option>
                          <option value="America/El_Salvador">America/El_Salvador</option>
                          <option value="America/Fort_Nelson">America/Fort_Nelson</option>
                          <option value="America/Fortaleza">America/Fortaleza</option>
                          <option value="America/Glace_Bay">America/Glace_Bay</option>
                          <option value="America/Godthab">America/Godthab</option>
                          <option value="America/Goose_Bay">America/Goose_Bay</option>
                          <option value="America/Grand_Turk">America/Grand_Turk</option>
                          <option value="America/Grenada">America/Grenada</option>
                          <option value="America/Guadeloupe">America/Guadeloupe</option>
                          <option value="America/Guatemala">America/Guatemala</option>
                          <option value="America/Guayaquil">America/Guayaquil</option>
                          <option value="America/Guyana">America/Guyana</option>
                          <option value="America/Halifax">America/Halifax</option>
                          <option value="America/Havana">America/Havana</option>
                          <option value="America/Hermosillo">America/Hermosillo</option>
                          <option value="America/Indiana/Indianapolis">America/Indiana/Indianapolis</option>
                          <option value="America/Indiana/Knox">America/Indiana/Knox</option>
                          <option value="America/Indiana/Marengo">America/Indiana/Marengo</option>
                          <option value="America/Indiana/Petersburg">America/Indiana/Petersburg</option>
                          <option value="America/Indiana/Tell_City">America/Indiana/Tell_City</option>
                          <option value="America/Indiana/Vevay">America/Indiana/Vevay</option>
                          <option value="America/Indiana/Vincennes">America/Indiana/Vincennes</option>
                          <option value="America/Indiana/Winamac">America/Indiana/Winamac</option>
                          <option value="America/Inuvik">America/Inuvik</option>
                          <option value="America/Iqaluit">America/Iqaluit</option>
                          <option value="America/Jamaica">America/Jamaica</option>
                          <option value="America/Juneau">America/Juneau</option>
                          <option value="America/Kentucky/Louisville">America/Kentucky/Louisville</option>
                          <option value="America/Kentucky/Monticello">America/Kentucky/Monticello</option>
                          <option value="America/Kralendijk">America/Kralendijk</option>
                          <option value="America/La_Paz">America/La_Paz</option>
                          <option value="America/Lima">America/Lima</option>
                          <option value="America/Los_Angeles">America/Los_Angeles</option>
                          <option value="America/Lower_Princes">America/Lower_Princes</option>
                          <option value="America/Maceio">America/Maceio</option>
                          <option value="America/Managua">America/Managua</option>
                          <option value="America/Manaus">America/Manaus</option>
                          <option value="America/Marigot">America/Marigot</option>
                          <option value="America/Martinique">America/Martinique</option>
                          <option value="America/Matamoros">America/Matamoros</option>
                          <option value="America/Mazatlan">America/Mazatlan</option>
                          <option value="America/Menominee">America/Menominee</option>
                          <option value="America/Merida">America/Merida</option>
                          <option value="America/Metlakatla">America/Metlakatla</option>
                          <option value="America/Mexico_City">America/Mexico_City</option>
                          <option value="America/Miquelon">America/Miquelon</option>
                          <option value="America/Moncton">America/Moncton</option>
                          <option value="America/Monterrey">America/Monterrey</option>
                          <option value="America/Montevideo">America/Montevideo</option>
                          <option value="America/Montserrat">America/Montserrat</option>
                          <option value="America/Nassau">America/Nassau</option>
                          <option value="America/New_York">America/New_York</option>
                          <option value="America/Nipigon">America/Nipigon</option>
                          <option value="America/Nome">America/Nome</option>
                          <option value="America/Noronha">America/Noronha</option>
                          <option value="America/North_Dakota/Beulah">America/North_Dakota/Beulah</option>
                          <option value="America/North_Dakota/Center">America/North_Dakota/Center</option>
                          <option value="America/North_Dakota/New_Salem">America/North_Dakota/New_Salem</option>
                          <option value="America/Ojinaga">America/Ojinaga</option>
                          <option value="America/Panama">America/Panama</option>
                          <option value="America/Pangnirtung">America/Pangnirtung</option>
                          <option value="America/Paramaribo">America/Paramaribo</option>
                          <option value="America/Phoenix">America/Phoenix</option>
                          <option value="America/Port-au-Prince">America/Port-au-Prince</option>
                          <option value="America/Port_of_Spain">America/Port_of_Spain</option>
                          <option value="America/Porto_Velho">America/Porto_Velho</option>
                          <option value="America/Puerto_Rico">America/Puerto_Rico</option>
                          <option value="America/Punta_Arenas">America/Punta_Arenas</option>
                          <option value="America/Rainy_River">America/Rainy_River</option>
                          <option value="America/Rankin_Inlet">America/Rankin_Inlet</option>
                          <option value="America/Recife">America/Recife</option>
                          <option value="America/Regina">America/Regina</option>
                          <option value="America/Resolute">America/Resolute</option>
                          <option value="America/Rio_Branco">America/Rio_Branco</option>
                          <option value="America/Santarem">America/Santarem</option>
                          <option value="America/Santiago">America/Santiago</option>
                          <option value="America/Santo_Domingo">America/Santo_Domingo</option>
                          <option value="America/Sao_Paulo">America/Sao_Paulo</option>
                          <option value="America/Scoresbysund">America/Scoresbysund</option>
                          <option value="America/Sitka">America/Sitka</option>
                          <option value="America/St_Barthelemy">America/St_Barthelemy</option>
                          <option value="America/St_Johns">America/St_Johns</option>
                          <option value="America/St_Kitts">America/St_Kitts</option>
                          <option value="America/St_Lucia">America/St_Lucia</option>
                          <option value="America/St_Thomas">America/St_Thomas</option>
                          <option value="America/St_Vincent">America/St_Vincent</option>
                          <option value="America/Swift_Current">America/Swift_Current</option>
                          <option value="America/Tegucigalpa">America/Tegucigalpa</option>
                          <option value="America/Thule">America/Thule</option>
                          <option value="America/Thunder_Bay">America/Thunder_Bay</option>
                          <option value="America/Tijuana">America/Tijuana</option>
                          <option value="America/Toronto">America/Toronto</option>
                          <option value="America/Tortola">America/Tortola</option>
                          <option value="America/Vancouver">America/Vancouver</option>
                          <option value="America/Whitehorse">America/Whitehorse</option>
                          <option value="America/Winnipeg">America/Winnipeg</option>
                          <option value="America/Yakutat">America/Yakutat</option>
                          <option value="America/Yellowknife">America/Yellowknife</option>
                          <option value="Asia/Aden">Asia/Aden</option>
                          <option value="Asia/Almaty">Asia/Almaty</option>
                          <option value="Asia/Amman">Asia/Amman</option>
                          <option value="Asia/Anadyr">Asia/Anadyr</option>
                          <option value="Asia/Aqtau">Asia/Aqtau</option>
                          <option value="Asia/Aqtobe">Asia/Aqtobe</option>
                          <option value="Asia/Ashgabat">Asia/Ashgabat</option>
                          <option value="Asia/Atyrau">Asia/Atyrau</option>
                          <option value="Asia/Baghdad">Asia/Baghdad</option>
                          <option value="Asia/Bahrain">Asia/Bahrain</option>
                          <option value="Asia/Baku">Asia/Baku</option>
                          <option value="Asia/Bangkok">Asia/Bangkok</option>
                          <option value="Asia/Barnaul">Asia/Barnaul</option>
                          <option value="Asia/Beirut">Asia/Beirut</option>
                          <option value="Asia/Bishkek">Asia/Bishkek</option>
                          <option value="Asia/Brunei">Asia/Brunei</option>
                          <option value="Asia/Chita">Asia/Chita</option>
                          <option value="Asia/Choibalsan">Asia/Choibalsan</option>
                          <option value="Asia/Colombo">Asia/Colombo</option>
                          <option value="Asia/Damascus">Asia/Damascus</option>
                          <option value="Asia/Dhaka">Asia/Dhaka</option>
                          <option value="Asia/Dili">Asia/Dili</option>
                          <option value="Asia/Dubai">Asia/Dubai</option>
                          <option value="Asia/Dushanbe">Asia/Dushanbe</option>
                          <option value="Asia/Famagusta">Asia/Famagusta</option>
                          <option value="Asia/Gaza">Asia/Gaza</option>
                          <option value="Asia/Hebron">Asia/Hebron</option>
                          <option value="Asia/Ho_Chi_Minh">Asia/Ho_Chi_Minh</option>
                          <option value="Asia/Hong_Kong">Asia/Hong_Kong</option>
                          <option value="Asia/Hovd">Asia/Hovd</option>
                          <option value="Asia/Irkutsk">Asia/Irkutsk</option>
                          <option value="Asia/Jakarta">Asia/Jakarta</option>
                          <option value="Asia/Jayapura">Asia/Jayapura</option>
                          <option value="Asia/Jerusalem">Asia/Jerusalem</option>
                          <option value="Asia/Kabul">Asia/Kabul</option>
                          <option value="Asia/Kamchatka">Asia/Kamchatka</option>
                          <option value="Asia/Karachi">Asia/Karachi</option>
                          <option value="Asia/Kathmandu">Asia/Kathmandu</option>
                          <option value="Asia/Khandyga">Asia/Khandyga</option>
                          <option value="Asia/Kolkata">Asia/Kolkata</option>
                          <option value="Asia/Krasnoyarsk">Asia/Krasnoyarsk</option>
                          <option value="Asia/Kuala_Lumpur">Asia/Kuala_Lumpur</option>
                          <option value="Asia/Kuching">Asia/Kuching</option>
                          <option value="Asia/Kuwait">Asia/Kuwait</option>
                          <option value="Asia/Macau">Asia/Macau</option>
                          <option value="Asia/Magadan">Asia/Magadan</option>
                          <option value="Asia/Makassar">Asia/Makassar</option>
                          <option value="Asia/Manila">Asia/Manila</option>
                          <option value="Asia/Muscat">Asia/Muscat</option>
                          <option value="Asia/Nicosia">Asia/Nicosia</option>
                          <option value="Asia/Novokuznetsk">Asia/Novokuznetsk</option>
                          <option value="Asia/Novosibirsk">Asia/Novosibirsk</option>
                          <option value="Asia/Omsk">Asia/Omsk</option>
                          <option value="Asia/Oral">Asia/Oral</option>
                          <option value="Asia/Phnom_Penh">Asia/Phnom_Penh</option>
                          <option value="Asia/Pontianak">Asia/Pontianak</option>
                          <option value="Asia/Pyongyang">Asia/Pyongyang</option>
                          <option value="Asia/Qatar">Asia/Qatar</option>
                          <option value="Asia/Qyzylorda">Asia/Qyzylorda</option>
                          <option value="Asia/Riyadh">Asia/Riyadh</option>
                          <option value="Asia/Sakhalin">Asia/Sakhalin</option>
                          <option value="Asia/Samarkand">Asia/Samarkand</option>
                          <option value="Asia/Seoul">Asia/Seoul</option>
                          <option value="Asia/Shanghai">Asia/Shanghai</option>
                          <option value="Asia/Singapore">Asia/Singapore</option>
                          <option value="Asia/Srednekolymsk">Asia/Srednekolymsk</option>
                          <option value="Asia/Taipei">Asia/Taipei</option>
                          <option value="Asia/Tashkent">Asia/Tashkent</option>
                          <option value="Asia/Tbilisi">Asia/Tbilisi</option>
                          <option value="Asia/Tehran">Asia/Tehran</option>
                          <option value="Asia/Thimphu">Asia/Thimphu</option>
                          <option value="Asia/Tokyo">Asia/Tokyo</option>
                          <option value="Asia/Tomsk">Asia/Tomsk</option>
                          <option value="Asia/Ulaanbaatar">Asia/Ulaanbaatar</option>
                          <option value="Asia/Urumqi">Asia/Urumqi</option>
                          <option value="Asia/Ust-Nera">Asia/Ust-Nera</option>
                          <option value="Asia/Vientiane">Asia/Vientiane</option>
                          <option value="Asia/Vladivostok">Asia/Vladivostok</option>
                          <option value="Asia/Yakutsk">Asia/Yakutsk</option>
                          <option value="Asia/Yangon">Asia/Yangon</option>
                          <option value="Asia/Yekaterinburg">Asia/Yekaterinburg</option>
                          <option value="Asia/Yerevan">Asia/Yerevan</option>
                          <option value="Europe/Amsterdam">Europe/Amsterdam</option>
                          <option value="Europe/Andorra">Europe/Andorra</option>
                          <option value="Europe/Astrakhan">Europe/Astrakhan</option>
                          <option value="Europe/Athens">Europe/Athens</option>
                          <option value="Europe/Belgrade">Europe/Belgrade</option>
                          <option value="Europe/Berlin">Europe/Berlin</option>
                          <option value="Europe/Bratislava">Europe/Bratislava</option>
                          <option value="Europe/Brussels">Europe/Brussels</option>
                          <option value="Europe/Bucharest">Europe/Bucharest</option>
                          <option value="Europe/Budapest">Europe/Budapest</option>
                          <option value="Europe/Busingen">Europe/Busingen</option>
                          <option value="Europe/Chisinau">Europe/Chisinau</option>
                          <option value="Europe/Copenhagen">Europe/Copenhagen</option>
                          <option value="Europe/Dublin">Europe/Dublin</option>
                          <option value="Europe/Gibraltar">Europe/Gibraltar</option>
                          <option value="Europe/Guernsey">Europe/Guernsey</option>
                          <option value="Europe/Helsinki">Europe/Helsinki</option>
                          <option value="Europe/Isle_of_Man">Europe/Isle_of_Man</option>
                          <option value="Europe/Istanbul">Europe/Istanbul</option>
                          <option value="Europe/Jersey">Europe/Jersey</option>
                          <option value="Europe/Kaliningrad">Europe/Kaliningrad</option>
                          <option value="Europe/Kiev">Europe/Kiev</option>
                          <option value="Europe/Kirov">Europe/Kirov</option>
                          <option value="Europe/Lisbon">Europe/Lisbon</option>
                          <option value="Europe/Ljubljana">Europe/Ljubljana</option>
                          <option value="Europe/London">Europe/London</option>
                          <option value="Europe/Luxembourg">Europe/Luxembourg</option>
                          <option value="Europe/Madrid">Europe/Madrid</option>
                          <option value="Europe/Malta">Europe/Malta</option>
                          <option value="Europe/Mariehamn">Europe/Mariehamn</option>
                          <option value="Europe/Minsk">Europe/Minsk</option>
                          <option value="Europe/Monaco">Europe/Monaco</option>
                          <option value="Europe/Moscow">Europe/Moscow</option>
                          <option value="Europe/Oslo">Europe/Oslo</option>
                          <option value="Europe/Paris">Europe/Paris</option>
                          <option value="Europe/Podgorica">Europe/Podgorica</option>
                          <option value="Europe/Prague">Europe/Prague</option>
                          <option value="Europe/Riga">Europe/Riga</option>
                          <option value="Europe/Rome">Europe/Rome</option>
                          <option value="Europe/Samara">Europe/Samara</option>
                          <option value="Europe/San_Marino">Europe/San_Marino</option>
                          <option value="Europe/Sarajevo">Europe/Sarajevo</option>
                          <option value="Europe/Saratov">Europe/Saratov</option>
                          <option value="Europe/Simferopol">Europe/Simferopol</option>
                          <option value="Europe/Skopje">Europe/Skopje</option>
                          <option value="Europe/Sofia">Europe/Sofia</option>
                          <option value="Europe/Stockholm">Europe/Stockholm</option>
                          <option value="Europe/Tallinn">Europe/Tallinn</option>
                          <option value="Europe/Tirane">Europe/Tirane</option>
                          <option value="Europe/Ulyanovsk">Europe/Ulyanovsk</option>
                          <option value="Europe/Uzhgorod">Europe/Uzhgorod</option>
                          <option value="Europe/Vaduz">Europe/Vaduz</option>
                          <option value="Europe/Vatican">Europe/Vatican</option>
                          <option value="Europe/Vienna">Europe/Vienna</option>
                          <option value="Europe/Vilnius">Europe/Vilnius</option>
                          <option value="Europe/Volgograd">Europe/Volgograd</option>
                          <option value="Europe/Warsaw">Europe/Warsaw</option>
                          <option value="Europe/Zagreb">Europe/Zagreb</option>
                          <option value="Europe/Zaporozhye">Europe/Zaporozhye</option>
                          <option value="Europe/Zurich">Europe/Zurich</option>
                          <option value="Australia/Adelaide">Australia/Adelaide</option>
                          <option value="Australia/Brisbane">Australia/Brisbane</option>
                          <option value="Australia/Broken_Hill">Australia/Broken_Hill</option>
                          <option value="Australia/Currie">Australia/Currie</option>
                          <option value="Australia/Darwin">Australia/Darwin</option>
                          <option value="Australia/Eucla">Australia/Eucla</option>
                          <option value="Australia/Hobart">Australia/Hobart</option>
                          <option value="Australia/Lindeman">Australia/Lindeman</option>
                          <option value="Australia/Lord_Howe">Australia/Lord_Howe</option>
                          <option value="Australia/Melbourne">Australia/Melbourne</option>
                          <option value="Australia/Perth">Australia/Perth</option>
                          <option value="Australia/Sydney">Australia/Sydney</option>
                        </optgroup>
                      </select>
                      <p className="text-xs text-muted-foreground mt-1">
                        Current timezone: {Intl.DateTimeFormat().resolvedOptions().timeZone}
                      </p>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="schedule-notes">Notes (Optional)</Label>
                    <Textarea
                      id="schedule-notes"
                      placeholder="Additional notes about this scheduled call..."
                      value={scheduleForm.notes}
                      onChange={(e) => setScheduleForm(prev => ({
                        ...prev,
                        notes: e.target.value
                      }))}
                      rows={3}
                    />
                  </div>

                  <Button 
                    type="submit" 
                    disabled={scheduleLoading}
                    className="w-full"
                  >
                    {scheduleLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Scheduling Call...
                      </>
                    ) : (
                      <>
                        <Calendar className="mr-2 h-4 w-4" />
                        Schedule Call
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Scheduled Calls List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Scheduled Calls
                </CardTitle>
                <CardDescription>
                  View and manage your scheduled interview calls
                </CardDescription>
              </CardHeader>
              <CardContent>
                {scheduledCalls.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No scheduled calls yet. Create your first scheduled call above.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {scheduledCalls.map((call) => (
                      <div key={call.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex justify-between items-start">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <h4 className="font-semibold">
                                {call.call_name || `Call to ${call.customer_number}`}
                              </h4>
                              <Badge className={getScheduleStatusColor(call.status)}>
                                {call.status}
                              </Badge>
                            </div>
                            <div className="text-sm text-muted-foreground space-y-1">
                              <p><strong>Customer:</strong> {call.customer_number}</p>
                              <p><strong>Scheduled:</strong> {formatScheduledTime(call.scheduled_time, call.timezone)} ({call.timezone || 'Local'})</p>
                              <p><strong>Assistant:</strong> {call.assistant_name}</p>
                              <p><strong>Phone:</strong> {call.phone_number_display}</p>
                              {call.notes && <p><strong>Notes:</strong> {call.notes}</p>}
                              {call.actual_call_id && (
                                <p><strong>Call ID:</strong> {call.actual_call_id}</p>
                              )}
                              {call.error_message && (
                                <p className="text-red-600"><strong>Error:</strong> {call.error_message}</p>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {call.status === 'scheduled' && (
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => handleDeleteScheduledCall(call.id)}
                              >
                                Cancel
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Transcripts Tab */}
        <TabsContent value="transcripts">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Call Transcripts
              </CardTitle>
              <CardDescription>
                View and search through all interview call transcripts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Search Bar */}
              <div className="flex gap-2">
                <div className="flex-1">
                  <Input
                    type="text"
                    placeholder="Search transcripts by customer number, status, content, or assistant..."
                    value={transcriptSearch}
                    onChange={(e) => setTranscriptSearch(e.target.value)}
                    className="w-full"
                  />
                </div>
                <Button onClick={loadAllCalls} disabled={transcriptLoading}>
                  {transcriptLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Refresh
                </Button>
              </div>

              {transcriptLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <div className="space-y-4">
                  {getFilteredCalls().length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      {allCalls.length === 0 ? 'No call transcripts found' : 'No calls match your search criteria'}
                    </div>
                  ) : (
                    <div className="grid gap-4">
                      {getFilteredCalls().map((call) => (
                        <Card key={call.id} className="border-l-4 border-l-blue-500">
                          <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <h4 className="font-semibold">
                                    Call to {call.customer_number}
                                  </h4>
                                  <Badge className={
                                    call.status === 'ended' ? 'bg-green-100 text-green-800' :
                                    call.status === 'failed' ? 'bg-red-100 text-red-800' :
                                    'bg-gray-100 text-gray-800'
                                  }>
                                    {call.status}
                                  </Badge>
                                  {call.outcome_status && (
                                    <Badge variant="outline">
                                      {call.outcome_status}
                                    </Badge>
                                  )}
                                </div>
                                <div className="text-sm text-gray-600 space-y-1">
                                  <p><strong>Date:</strong> {new Date(call.created_at).toLocaleString()}</p>
                                  <p><strong>Assistant:</strong> {call.assistant?.name || 'Unknown'}</p>
                                  {call.duration_seconds && (
                                    <p><strong>Duration:</strong> {Math.floor(call.duration_seconds / 60)}m {call.duration_seconds % 60}s</p>
                                  )}
                                  {call.cost && <p><strong>Cost:</strong> ${call.cost}</p>}
                                </div>
                              </div>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => loadCallTranscript(call.vapi_call_id)}
                              >
                                View Details
                              </Button>
                            </div>
                          </CardHeader>
                          
                          {/* Show transcript if available */}
                          {call.transcript_text && (
                            <CardContent className="pt-0">
                              <div className="space-y-2">
                                <h5 className="font-medium text-gray-900">Transcript Preview:</h5>
                                <div className="bg-gray-50 rounded-lg p-3 max-h-32 overflow-y-auto">
                                  <pre className="whitespace-pre-wrap text-xs text-gray-700">
                                    {call.transcript_text.length > 300 
                                      ? `${call.transcript_text.substring(0, 300)}...` 
                                      : call.transcript_text
                                    }
                                  </pre>
                                </div>
                                {call.transcript_text.length > 300 && (
                                  <Button
                                    variant="link"
                                    size="sm"
                                    onClick={() => loadCallTranscript(call.vapi_call_id)}
                                    className="p-0 h-auto"
                                  >
                                    Read full transcript →
                                  </Button>
                                )}
                              </div>
                            </CardContent>
                          )}
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Selected Call Details Modal */}
              {selectedCall && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                  <div className="bg-white rounded-lg max-w-4xl w-full max-h-90vh overflow-hidden">
                    <div className="p-6 border-b">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-semibold">
                            Call Details: {selectedCall.customer_number || selectedCall.customer?.number || selectedCall.phoneNumber}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {selectedCall.createdAt && new Date(selectedCall.createdAt).toLocaleString()}
                          </p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedCall(null)}
                        >
                          Close
                        </Button>
                      </div>
                    </div>
                    
                    <div className="p-6 overflow-y-auto max-h-96">
                      {/* Call Information */}
                      <div className="space-y-4 mb-6">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="text-sm font-medium text-gray-500">Status</label>
                            <p className="mt-1">{selectedCall.status}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium text-gray-500">Duration</label>
                            <p className="mt-1">{selectedCall.duration_formatted || 'N/A'}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium text-gray-500">Cost</label>
                            <p className="mt-1">${selectedCall.cost || '0.00'}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium text-gray-500">Outcome</label>
                            <p className="mt-1">{selectedCall.outcome?.status || 'N/A'}</p>
                          </div>
                        </div>
                      </div>

                      {/* Full Transcript */}
                      {selectedCall.transcript_text && (
                        <div className="space-y-2">
                          <h4 className="font-semibold text-gray-900">Full Transcript</h4>
                          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                            <pre className="whitespace-pre-wrap text-sm text-gray-700">
                              {formatTranscriptText(selectedCall.transcript_text)}
                            </pre>
                          </div>
                        </div>
                      )}

                      {/* Structured Transcript */}
                      {selectedCall.transcript && Array.isArray(selectedCall.transcript) && (
                        <div className="space-y-2 mt-4">
                          <h4 className="font-semibold text-gray-900">Conversation Flow</h4>
                          <div className="space-y-2">
                            {selectedCall.transcript.map((item, index) => (
                              <div key={index} className={`p-3 rounded-lg ${
                                item.role === 'assistant' 
                                  ? 'bg-blue-50 border-l-4 border-blue-500' 
                                  : 'bg-green-50 border-l-4 border-green-500'
                              }`}>
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-xs font-semibold uppercase text-gray-600">
                                    {item.role}
                                  </span>
                                  {item.timestamp && (
                                    <span className="text-xs text-gray-500">
                                      {item.timestamp}
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm">{item.message}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {!selectedCall.transcript_text && !selectedCall.transcript && (
                        <div className="text-center py-8 text-gray-500">
                          No transcript available for this call
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    );
  } catch (error) {
    console.error('Error rendering InterviewDashboard:', error);
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-red-600">Error Loading Interview Dashboard</h1>
        <p className="text-gray-600 mt-2">An error occurred while loading the interview dashboard.</p>
        <pre className="mt-4 p-4 bg-gray-100 rounded text-sm overflow-auto">
          {error.toString()}
        </pre>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded"
        >
          Refresh Page
        </button>
      </div>
    );
  }
};

export default InterviewDashboard;

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
import { Loader2, Phone, User, Settings, Shield, CheckCircle, XCircle, Calendar, Clock } from 'lucide-react';
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
  scheduleCall,
  getScheduledCalls,
  deleteScheduledCall
} from '../utils/interviewApi';
import { getCampaigns } from '../utils/campaign';

const InterviewDashboard = () => {
  const { campaignId } = useParams(); // Get campaign ID from URL
  
  // Campaign State
  const [currentCampaign, setCurrentCampaign] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  
  // API Configuration State
  const [apiConfig, setApiConfig] = useState({
    twilio_account_sid: '',
    twilio_auth_token: '',
    vapi_api_key: '',
    twilio_configured: false,
    vapi_configured: false
  });
  const [configLoading, setConfigLoading] = useState(false);
  const [configMessage, setConfigMessage] = useState('');

  // Assistant State
  const [assistantForm, setAssistantForm] = useState({
    name: 'Professional Interviewer',
    first_message: 'Good day, I\'ll be conducting your interview today. Let\'s begin.',
    voice_provider: 'openai',
    voice_id: 'nova',
    model_provider: 'openai',
    model: 'gpt-4',
    knowledge_text: '',
    knowledge_urls: '',
    campaign_id: campaignId || null
  });
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [assistantMessage, setAssistantMessage] = useState('');
  const [assistants, setAssistants] = useState([]);

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

  // Scheduled Call State
  const [scheduleForm, setScheduleForm] = useState({
    customer_number: '',
    twilio_phone_number_id: '',
    vapi_assistant_id: '',
    scheduled_time: '',
    call_name: '',
    notes: ''
  });
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [scheduledCalls, setScheduledCalls] = useState([]);
  const [scheduleMessage, setScheduleMessage] = useState('');

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
        vapi_api_key: apiConfig.vapi_api_key
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
        vapi_api_key: ''
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
      const response = await createAssistant(assistantForm);
      
      if (response.data.success) {
        setAssistantMessage('Professional Interviewer Created Successfully!');
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

    try {
      const response = await makeCall(callForm);
      if (response.data.success) {
        setCurrentCall(response.data.call_data);
        await refreshCallDetails();
      } else {
        alert(`Error: ${response.data.error}`);
      }
    } catch (error) {
      alert(`Error: ${error.response?.data?.error || error.message}`);
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

      // Validate scheduled time is in the future
      const scheduledDate = new Date(scheduleForm.scheduled_time);
      if (scheduledDate <= new Date()) {
        setScheduleMessage('Scheduled time must be in the future');
        setScheduleLoading(false);
        return;
      }

      const response = await scheduleCall(scheduleForm);
      if (response.data.success) {
        setScheduleMessage('Call scheduled successfully!');
        setScheduleForm({
          customer_number: '',
          twilio_phone_number_id: '',
          vapi_assistant_id: '',
          scheduled_time: '',
          call_name: '',
          notes: ''
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

  const formatScheduledTime = (timeString) => {
    const date = new Date(timeString);
    // If the date string ends with 'Z' or has timezone info, it's already in UTC
    // Convert to local time for display
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  };

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
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="config" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Configuration
          </TabsTrigger>
          <TabsTrigger value="assistant" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Assistant
          </TabsTrigger>
          <TabsTrigger value="phones" className="flex items-center gap-2">
            <Phone className="h-4 w-4" />
            Phone Numbers
          </TabsTrigger>
          <TabsTrigger value="calls" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Make Calls
          </TabsTrigger>
          <TabsTrigger value="scheduled" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Schedule Calls
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
                Configure your Twilio and Vapi API credentials
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <span>Twilio Configured:</span>
                  {apiConfig.twilio_configured ? (
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
                  {apiConfig.vapi_configured ? (
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
                      onChange={(e) => setAssistantForm(prev => ({
                        ...prev,
                        first_message: e.target.value
                      }))}
                      placeholder="Good day, I'll be conducting your interview today."
                    />
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
                      <option value="playht">Play.ht</option>
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
                    >
                      <option value="nova">Nova (Professional Female)</option>
                      <option value="onyx">Onyx (Professional Male)</option>
                      <option value="alloy">Alloy (Neutral)</option>
                      <option value="echo">Echo (Clear)</option>
                      <option value="fable">Fable (Warm)</option>
                      <option value="shimmer">Shimmer (Gentle)</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="knowledgeText">Interview Knowledge Base (Text)</Label>
                  <Textarea
                    id="knowledgeText"
                    rows={6}
                    value={assistantForm.knowledge_text}
                    onChange={(e) => setAssistantForm(prev => ({
                      ...prev,
                      knowledge_text: e.target.value
                    }))}
                    placeholder="Enter interview topics, company information, role requirements, or specific areas to focus on during the interview..."
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
                            onClick={() => setCallForm(prev => ({
                              ...prev,
                              vapi_assistant_id: assistant.vapi_assistant_id
                            }))}
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
                          onClick={() => setCallForm(prev => ({
                            ...prev,
                            twilio_phone_number_id: number.id
                          }))}
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

                  {callDetails && (
                    <div className="space-y-2 text-sm">
                      <p><strong>Call ID:</strong> {callDetails.id}</p>
                      <p><strong>Customer:</strong> {callDetails.customer}</p>
                      {callDetails.cost && (
                        <p><strong>Cost:</strong> ${callDetails.cost.toFixed(4)}</p>
                      )}
                      {callDetails.duration_formatted && (
                        <p><strong>Duration:</strong> {callDetails.duration_formatted}</p>
                      )}
                      {callDetails.outcome && (
                        <p><strong>Description:</strong> {callDetails.outcome.description}</p>
                      )}
                    </div>
                  )}

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
                              <p><strong>Scheduled:</strong> {formatScheduledTime(call.scheduled_time)}</p>
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
      </Tabs>
    </div>
  );
};

export default InterviewDashboard;

import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogTrigger, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Plus, PhoneCall, Mic, List, Phone, Settings, User, Clock, DollarSign, Search, Eye, FileText, Loader2 } from "lucide-react"
import { createCampaigns, getCampaigns } from "../utils/campaign"
import { getCalls, getCallDetails } from "../utils/interviewApi"
import { Description } from "@radix-ui/react-dialog"

export default function Dashboard() {
  const [campaigns, setCampaigns] = useState([])
  const [selectedCampaign, setSelectedCampaign] = useState(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [formData, setFormData] = useState({ name: '', description: '' })
  
  // Call and Transcript State
  const [calls, setCalls] = useState([])
  const [filteredCalls, setFilteredCalls] = useState([])
  const [filteredTranscripts, setFilteredTranscripts] = useState([])
  const [callsLoading, setCallsLoading] = useState(false)
  const [selectedCall, setSelectedCall] = useState(null)
  const [showCallDialog, setShowCallDialog] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [transcriptSearchTerm, setTranscriptSearchTerm] = useState("")
  
  const navigate = useNavigate()

  // Fetch campaigns
  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const campaigns = await getCampaigns()
        console.log('Loaded campaigns:', campaigns.data)
        setCampaigns(campaigns.data || [])
      } catch (error) {
        console.error("Failed to fetch campaigns:", error)
        setCampaigns([])
      }
    }
    fetchCampaigns()
  }, [])

  // Fetch calls
  useEffect(() => {
    const fetchCalls = async () => {
      setCallsLoading(true)
      try {
        const response = await getCalls()
        console.log('Loaded calls:', response.data)
        setCalls(response.data || [])
      } catch (error) {
        console.error("Failed to fetch calls:", error)
        setCalls([])
      } finally {
        setCallsLoading(false)
      }
    }
    fetchCalls()
  }, [])

  // Filter calls based on search and status
  useEffect(() => {
    let filtered = calls.filter(call => {
      const matchesSearch = searchTerm === "" || 
        call.customer_number?.includes(searchTerm) ||
        (call.assistant_name || call.assistant?.name || '')?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (call.campaign_name || call.campaign?.name || '')?.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = statusFilter === "all" || call.outcome_status === statusFilter
      
      return matchesSearch && matchesStatus
    })
    setFilteredCalls(filtered)
  }, [calls, searchTerm, statusFilter])

  // Filter transcripts based on search
  useEffect(() => {
    const callsWithTranscripts = calls.filter(call => 
      call.transcript_text && call.transcript_text.trim() !== ""
    )
    
    let filtered = callsWithTranscripts.filter(call => {
      const matchesSearch = transcriptSearchTerm === "" ||
        call.transcript_text?.toLowerCase().includes(transcriptSearchTerm.toLowerCase()) ||
        call.customer_number?.includes(transcriptSearchTerm) ||
        (call.assistant_name || call.assistant?.name || '')?.toLowerCase().includes(transcriptSearchTerm.toLowerCase())
      
      return matchesSearch
    })
    setFilteredTranscripts(filtered)
  }, [calls, transcriptSearchTerm])

  // Utility functions
  const getStatusBadgeVariant = (status) => {
    const statusColors = {
      'answered': 'default',
      'answered-brief': 'secondary',
      'voicemail': 'outline', 
      'no-answer': 'destructive',
      'busy': 'destructive',
      'declined': 'destructive',
      'failed': 'destructive',
      'in-progress': 'default',
      'ringing': 'secondary',
      'completed': 'default',
      'unknown': 'outline'
    }
    return statusColors[status] || 'outline'
  }

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A'
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const formatCost = (cost) => {
    if (!cost) return 'N/A'
    return `$${parseFloat(cost).toFixed(4)}`
  }

  const handleViewCallDetails = async (callId) => {
    try {
      const response = await getCallDetails(callId)
      setSelectedCall(response.data)
      setShowCallDialog(true)
    } catch (error) {
      console.error("Failed to fetch call details:", error)
    }
  }

  const handleCreateCampaign = async (event) => {
    event.preventDefault()
    if (!formData.name.trim()) {
      alert("Campaign name is required.")
      return
    }
    const campaignData = {
      name: formData['name'],
      description: formData['description'],
    }
    console.log("Creating campaign with data:", campaignData)
    // Placeholder for actual API call to create campaign
    try {
      await createCampaigns(campaignData)
      setShowCreateDialog(false)
      const updatedCampaigns = await getCampaigns()
      setCampaigns(updatedCampaigns.data || [])
    } catch (error) {
      console.error("Failed to create campaign:", error)
    }
  }
  const handleSelectCampaign = (campaign) => {
    setSelectedCampaign(campaign)
    navigate(`/interview/${campaign.id}`)
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="mr-2 h-4 w-4" /> New Campaign
        </Button>
      </div>

      {/* Quick Access Cards */}
      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate('/interview')}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Interview System
            </CardTitle>
            <Phone className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">AI Interviews</div>
            <p className="text-xs text-muted-foreground">
              Configure and manage smart AI-powered interviews
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Calls
            </CardTitle>
            <PhoneCall className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {calls.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Total calls made across all campaigns
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Campaigns
            </CardTitle>
            <List className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{campaigns.length}</div>
            <p className="text-xs text-muted-foreground">
              {campaigns.length > 0 ? 'All systems running' : 'No active campaigns'}
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="campaigns" className="w-full">
        <TabsList>
          <TabsTrigger value="campaigns"><List className="mr-2 h-4 w-4" /> Campaigns</TabsTrigger>
          <TabsTrigger value="calls"><PhoneCall className="mr-2 h-4 w-4" /> Calls</TabsTrigger>
          <TabsTrigger value="transcripts"><Mic className="mr-2 h-4 w-4" /> Transcripts</TabsTrigger>
        </TabsList>

        <TabsContent value="campaigns">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {campaigns.map((c) => (
              <Card key={c.id} onClick={() => handleSelectCampaign(c)} className="cursor-pointer">
                <CardHeader>
                  <CardTitle>{c.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Calls Made: {(() => {
                      const campaignCalls = calls.filter(call => {
                        const match = call.campaign_id === c.id || 
                                     (call.campaign && call.campaign.id === c.id) ||
                                     call.campaign_name === c.name ||
                                     (call.assistant && call.assistant.campaign_id === c.id);
                        if (match) {
                          console.log(`Call ${call.id} matches campaign ${c.name} (${c.id}):`, {
                            call_campaign_id: call.campaign_id,
                            call_campaign_object: call.campaign,
                            call_campaign_name: call.campaign_name,
                            assistant_campaign_id: call.assistant?.campaign_id
                          });
                        }
                        return match;
                      });
                      console.log(`Campaign "${c.name}" (ID: ${c.id}) has ${campaignCalls.length} calls`);
                      return campaignCalls.length;
                    })()}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="calls" className="space-y-4">
          {/* Call Filters */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex flex-col sm:flex-row gap-2 flex-1">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search calls by number, assistant, or campaign..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-input bg-background rounded-md text-sm"
              >
                <option value="all">All Statuses</option>
                <option value="answered">Answered</option>
                <option value="answered-brief">Answered (Brief)</option>
                <option value="voicemail">Voicemail</option>
                <option value="no-answer">No Answer</option>
                <option value="busy">Busy</option>
                <option value="declined">Declined</option>
                <option value="failed">Failed</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div className="text-sm text-muted-foreground">
              {filteredCalls.length} of {calls.length} calls
            </div>
          </div>

          {/* Call List */}
          {callsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin mr-2" />
              Loading calls...
            </div>
          ) : filteredCalls.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              {calls.length === 0 ? 'No calls found' : 'No calls match your filters'}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredCalls.map((call) => (
                <Card key={call.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-medium">{call.customer_number}</span>
                          <Badge variant={getStatusBadgeVariant(call.outcome_status)}>
                            {call.outcome_status || call.status}
                          </Badge>
                          {(call.campaign_name || call.campaign?.name) && (
                            <Badge variant="outline">{call.campaign_name || call.campaign?.name}</Badge>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground space-y-1">
                          <div className="flex items-center gap-4 flex-wrap">
                            <span className="flex items-center gap-1">
                              <User className="h-3 w-3" />
                              {call.assistant_name || call.assistant?.name || 'Unknown Assistant'}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatDateTime(call.created_at)}
                            </span>
                            <span className="flex items-center gap-1">
                              <Phone className="h-3 w-3" />
                              {formatDuration(call.duration_seconds)}
                            </span>
                            <span className="flex items-center gap-1">
                              <DollarSign className="h-3 w-3" />
                              {formatCost(call.cost)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewCallDetails(call.vapi_call_id)}
                        className="flex items-center gap-1"
                      >
                        <Eye className="h-3 w-3" />
                        View Details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="transcripts" className="space-y-4">
          {/* Transcript Search */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search transcripts..."
                value={transcriptSearchTerm}
                onChange={(e) => setTranscriptSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
            <div className="text-sm text-muted-foreground">
              {filteredTranscripts.length} transcripts available
            </div>
          </div>

          {/* Transcript List */}
          {filteredTranscripts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              {calls.filter(c => c.transcript_text).length === 0 
                ? 'No transcripts available' 
                : 'No transcripts match your search'}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredTranscripts.map((call) => (
                <Card key={call.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{call.customer_number}</CardTitle>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span>{formatDateTime(call.created_at)}</span>
                          <span>•</span>
                          <span>{call.assistant_name || call.assistant?.name}</span>
                          <span>•</span>
                          <span>{formatDuration(call.duration_seconds)}</span>
                          {(call.campaign_name || call.campaign?.name) && (
                            <>
                              <span>•</span>
                              <Badge variant="outline" className="text-xs">
                                {call.campaign_name || call.campaign?.name}
                              </Badge>
                            </>
                          )}
                        </div>
                      </div>
                      <Badge variant={getStatusBadgeVariant(call.outcome_status)}>
                        {call.outcome_status || call.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 justify-between">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium text-sm">Transcript</span>
                        </div>
                        {call.has_recording && call.recording_file_url && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              const audio = new Audio(call.recording_file_url);
                              audio.play().catch(err => {
                                console.error('Failed to play audio:', err);
                                alert('Failed to play recording. Please try again.');
                              });
                            }}
                            className="flex items-center gap-1"
                          >
                            <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                            </svg>
                            Play
                          </Button>
                        )}
                      </div>
                      <div className="bg-muted/30 rounded-md p-3 max-h-64 overflow-y-auto">
                        <pre className="text-sm whitespace-pre-wrap font-sans">
                          {call.transcript_text || 'No transcript available'}
                        </pre>
                      </div>
                      {call.outcome_description && (
                        <div className="text-sm text-muted-foreground">
                          <strong>Outcome:</strong> {call.outcome_description}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Campaign Creation Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogTrigger asChild></DialogTrigger>
        <DialogContent>
          <DialogTitle>Create New Campaign</DialogTitle>
          <form onSubmit={handleCreateCampaign} className="space-y-4">
            <Input id="name" onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))} placeholder="Campaign Name" required />
            <Textarea onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))} id="description" placeholder="Description / Purpose" />
            <Button type="submit" className="w-full">Create</Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Call Details Dialog */}
      <Dialog open={showCallDialog} onOpenChange={setShowCallDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogTitle>Call Details</DialogTitle>
          {selectedCall && (
            <div className="space-y-6">
              {/* Call Overview */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Call Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Phone Number:</span>
                      <span className="font-medium">{selectedCall.customer_number || selectedCall.customer}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Status:</span>
                      <Badge variant={getStatusBadgeVariant(selectedCall.outcome_status || selectedCall.outcome?.status)}>
                        {selectedCall.outcome_status || selectedCall.outcome?.status || selectedCall.status}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Assistant:</span>
                      <span className="font-medium">{selectedCall.assistant_name || selectedCall.assistant?.name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Campaign:</span>
                      <span className="font-medium">{selectedCall.campaign_name || selectedCall.campaign?.name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="font-medium">{formatDuration(selectedCall.duration_seconds) || selectedCall.duration_formatted}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Cost:</span>
                      <span className="font-medium">{formatCost(selectedCall.cost)}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Timeline</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Created:</span>
                      <span className="font-medium">{formatDateTime(selectedCall.created_at || selectedCall.createdAt)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Started:</span>
                      <span className="font-medium">{formatDateTime(selectedCall.started_at || selectedCall.startedAt)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Ended:</span>
                      <span className="font-medium">{formatDateTime(selectedCall.ended_at || selectedCall.endedAt)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">End Reason:</span>
                      <span className="font-medium">{selectedCall.end_reason || selectedCall.endReason || 'N/A'}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Cost Breakdown */}
              {(selectedCall.cost_breakdown || selectedCall.costBreakdown) && Object.keys(selectedCall.cost_breakdown || selectedCall.costBreakdown).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Cost Breakdown</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(selectedCall.cost_breakdown || selectedCall.costBreakdown).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-muted-foreground capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="font-medium">${parseFloat(value).toFixed(4)}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Outcome Description */}
              {(selectedCall.outcome_description || selectedCall.outcome?.description) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Outcome Description</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">{selectedCall.outcome_description || selectedCall.outcome?.description}</p>
                  </CardContent>
                </Card>
              )}

              {/* Transcript */}
              {(selectedCall.transcript_text || selectedCall.transcript) && (
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0">
                    <CardTitle className="text-lg">Transcript</CardTitle>
                    {selectedCall.has_recording && selectedCall.recording_file_url && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          const audio = new Audio(selectedCall.recording_file_url);
                          audio.play().catch(err => {
                            console.error('Failed to play audio:', err);
                            alert('Failed to play recording. Please try again.');
                          });
                        }}
                        className="flex items-center gap-2"
                      >
                        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                        </svg>
                        Play Recording
                      </Button>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted/30 rounded-md p-4 max-h-96 overflow-y-auto">
                      <pre className="text-sm whitespace-pre-wrap font-sans">
                        {selectedCall.transcript_text || (Array.isArray(selectedCall.transcript) 
                          ? selectedCall.transcript.map(item => `${item.role}: ${item.message}`).join('\n')
                          : selectedCall.transcript
                        )}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Raw JSON Data */}
              {selectedCall.raw_call_data && Object.keys(selectedCall.raw_call_data).length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Raw Call Data</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-muted/30 rounded-md p-4 max-h-96 overflow-y-auto">
                      <pre className="text-xs font-mono">
                        {JSON.stringify(selectedCall.raw_call_data, null, 2)}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

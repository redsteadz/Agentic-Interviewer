import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Dialog, DialogTrigger, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { Plus, PhoneCall, Mic, List, Phone, Settings, User } from "lucide-react"

export default function Dashboard() {
  const [campaigns, setCampaigns] = useState([])
  const [selectedCampaign, setSelectedCampaign] = useState(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const navigate = useNavigate()

  // Placeholder fetch logic, replace with real API later
  useEffect(() => {
    setCampaigns([
      { id: 1, name: "Onboarding Interview", callCount: 10 },
      { id: 2, name: "Follow-up Calls", callCount: 5 },
    ])
  }, [])

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
              {campaigns.reduce((total, c) => total + c.callCount, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              +20.1% from last month
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
              <Card key={c.id} onClick={() => setSelectedCampaign(c)} className="cursor-pointer">
                <CardHeader>
                  <CardTitle>{c.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">Calls Made: {c.callCount}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="calls">
          <p className="text-muted-foreground">(Call list will be displayed here)</p>
        </TabsContent>

        <TabsContent value="transcripts">
          <p className="text-muted-foreground">(Transcript viewer goes here)</p>
        </TabsContent>
      </Tabs>

      {/* Campaign Creation Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogTrigger asChild></DialogTrigger>
        <DialogContent>
          <DialogTitle>Create New Campaign</DialogTitle>
          <form className="space-y-4">
            <Input placeholder="Campaign Name" required />
            <Textarea placeholder="Description / Purpose" />
            <Button type="submit" className="w-full">Create</Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

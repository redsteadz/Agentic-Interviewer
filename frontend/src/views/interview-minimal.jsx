import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';

const InterviewMinimal = () => {
  console.log('InterviewMinimal component rendering...');
  
  const [callForm, setCallForm] = useState({
    customer_number: '',
    twilio_phone_number_id: '',
    vapi_assistant_id: ''
  });
  const [callLoading, setCallLoading] = useState(false);
  const [callMessage, setCallMessage] = useState('');

  const handleMakeCall = async (e) => {
    e.preventDefault();
    console.log('Begin Professional Interview clicked');
    setCallMessage('Test call initiated - this is working!');
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Interview Dashboard - Minimal Test</h1>
      
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Start Interview Call
          </CardTitle>
          <CardDescription>
            Test version of the Begin Professional Interview functionality
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleMakeCall} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="customerNumber">Phone Number</Label>
              <Input
                id="customerNumber"
                type="tel"
                value={callForm.customer_number}
                onChange={(e) => setCallForm(prev => ({ ...prev, customer_number: e.target.value }))}
                placeholder="+1234567890"
              />
            </div>

            <Button type="submit" disabled={callLoading} className="w-full">
              {callLoading && <span className="mr-2">Loading...</span>}
              🚀 Begin Professional Interview
            </Button>
          </form>

          {callMessage && (
            <div className="mt-4 p-3 bg-green-100 border border-green-400 rounded">
              {callMessage}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default InterviewMinimal;
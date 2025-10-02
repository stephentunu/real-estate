
import React, { useState } from 'react';
import { CreditCard, Plus, Edit, Trash2, Calendar, DollarSign } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import DashboardLayout from '@/components/DashboardLayout';
import { useToast } from '@/hooks/use-toast';

const PaymentsPage = () => {
  const { toast } = useToast();
  const [isAddingCard, setIsAddingCard] = useState(false);
  
  // Mock payment data
  const paymentMethods = [
    {
      id: '1',
      type: 'Visa',
      lastFour: '4242',
      expiryDate: '12/25',
      isDefault: true
    },
    {
      id: '2',
      type: 'Mastercard',
      lastFour: '8888',
      expiryDate: '08/26',
      isDefault: false
    }
  ];

  const transactions = [
    {
      id: '1',
      method: 'Rent Payment',
      description: 'Monthly rent for Westlands Apartment',
      amount: 85000,
      date: '2023-06-01',
      status: 'Completed'
    },
    {
      id: '2',
      method: 'Security Deposit',
      description: 'Security deposit for Kilimani Townhouse',
      amount: 120000,
      date: '2023-05-15',
      status: 'Completed'
    },
    {
      id: '3',
      method: 'Application Fee',
      description: 'Application processing fee',
      amount: 2500,
      date: '2023-05-10',
      status: 'Pending'
    }
  ];

  const [newCard, setNewCard] = useState({
    cardName: '',
    cardNumber: '',
    expiryDate: '',
    cvv: ''
  });

  const handleAddCard = () => {
    setIsAddingCard(false);
    setNewCard({ cardName: '', cardNumber: '', expiryDate: '', cvv: '' });
    toast({
      title: "Payment method added",
      description: "Your new payment method has been added successfully.",
    });
  };

  const handleDeleteCard = (cardId: string) => {
    toast({
      title: "Payment method removed",
      description: "The payment method has been removed from your account.",
    });
  };

  const handleSetDefault = (cardId: string) => {
    toast({
      title: "Default payment method updated",
      description: "This payment method is now your default.",
    });
  };

  return (
    <DashboardLayout title="Payments">
      <div className="space-y-6">
        {/* Payment Methods */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Payment Methods</CardTitle>
              <p className="text-sm text-muted-foreground">Manage your saved payment methods</p>
            </div>
            <Dialog open={isAddingCard} onOpenChange={setIsAddingCard}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Card
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add New Payment Method</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Cardholder Name</label>
                    <Input 
                      value={newCard.cardName}
                      onChange={(e) => setNewCard({...newCard, cardName: e.target.value})}
                      placeholder="John Doe"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Card Number</label>
                    <Input 
                      value={newCard.cardNumber}
                      onChange={(e) => setNewCard({...newCard, cardNumber: e.target.value})}
                      placeholder="1234 5678 9012 3456"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium mb-1 block">Expiry Date</label>
                      <Input 
                        value={newCard.expiryDate}
                        onChange={(e) => setNewCard({...newCard, expiryDate: e.target.value})}
                        placeholder="MM/YY"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-1 block">CVV</label>
                      <Input 
                        value={newCard.cvv}
                        onChange={(e) => setNewCard({...newCard, cvv: e.target.value})}
                        placeholder="123"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end space-x-2 pt-4">
                    <Button variant="outline" onClick={() => setIsAddingCard(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddCard}>
                      Add Card
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {paymentMethods.map((method) => (
                <div key={method.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center">
                    <CreditCard className="h-8 w-8 text-rental-500 mr-3" />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{method.type} •••• {method.lastFour}</span>
                        {method.isDefault && (
                          <Badge variant="secondary">Default</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">Expires {method.expiryDate}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {!method.isDefault && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleSetDefault(method.id)}
                      >
                        Set as Default
                      </Button>
                    )}
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeleteCard(method.id)}
                      className="text-red-500 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Transaction History */}
        <Card>
          <CardHeader>
            <CardTitle>Transaction History</CardTitle>
            <p className="text-sm text-muted-foreground">Your recent payment transactions</p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-rental-100 dark:bg-rental-800 flex items-center justify-center mr-3">
                      <DollarSign className="h-5 w-5 text-rental-600" />
                    </div>
                    <div>
                      <div className="font-medium">{transaction.method}</div>
                      <p className="text-sm text-muted-foreground">{transaction.description}</p>
                      <div className="flex items-center text-xs text-muted-foreground mt-1">
                        <Calendar className="h-3 w-3 mr-1" />
                        {transaction.date}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">
                      KSh {transaction.amount.toLocaleString()}
                    </div>
                    <Badge 
                      variant={transaction.status === 'Completed' ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {transaction.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default PaymentsPage;

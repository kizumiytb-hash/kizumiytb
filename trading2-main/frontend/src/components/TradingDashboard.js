import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { 
  TrendingUp, TrendingDown, DollarSign, BarChart3, Zap, Shield, Wallet, Plus, History, 
  CreditCard, ArrowUpCircle, ArrowDownCircle, Building2, CheckCircle, AlertCircle, Clock, 
  LogOut, User, Settings
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const TradingDashboard = () => {
  const { user, logout, apiCall } = useAuth();
  
  const [prices, setPrices] = useState([]);
  const [currentAccount, setCurrentAccount] = useState(null);
  const [positions, setPositions] = useState([]);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [orderForm, setOrderForm] = useState({
    symbol: 'EURUSD',
    orderType: 'buy',
    volume: 0.01,
    leverage: 'unlimited'
  });
  const [accountType, setAccountType] = useState('demo');
  const [transactionForm, setTransactionForm] = useState({
    amount: '',
    description: ''
  });
  const [withdrawalForm, setWithdrawalForm] = useState({
    amount: '',
    description: ''
  });
  const [isTransactionOpen, setIsTransactionOpen] = useState(false);
  const [isWithdrawalOpen, setIsWithdrawalOpen] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);

  // Helper function to get URL parameters
  const getUrlParameter = (name) => {
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(window.location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
  };

  // Check for payment return and poll status
  useEffect(() => {
    const sessionId = getUrlParameter('session_id');
    const paymentReturn = getUrlParameter('payment');
    
    if (sessionId && paymentReturn === 'success') {
      setIsProcessingPayment(true);
      setPaymentStatus('checking');
      pollPaymentStatus(sessionId);
    } else if (paymentReturn === 'cancelled') {
      setPaymentStatus('cancelled');
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  // Poll payment status
  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 8;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      setPaymentStatus('timeout');
      setIsProcessingPayment(false);
      return;
    }

    try {
      const response = await apiCall(`/api/stripe/checkout/status/${sessionId}`);
      if (!response.ok) {
        throw new Error('Failed to check payment status');
      }

      const data = await response.json();
      
      if (data.payment_status === 'paid') {
        setPaymentStatus('completed');
        setIsProcessingPayment(false);
        
        // Clean URL and show success message
        window.history.replaceState({}, document.title, window.location.pathname);
        
        const amount = (data.amount_total / 100).toFixed(2); // Convert from cents
        alert(`Paiement réussi! Montant: ${amount}€`);
        
        // Refresh account data
        setTimeout(() => {
          window.location.reload();
        }, 1000);
        
        return;
      } else if (data.status === 'expired') {
        setPaymentStatus('expired');
        setIsProcessingPayment(false);
        return;
      }

      // If payment is still pending, continue polling
      setPaymentStatus('processing');
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setPaymentStatus('error');
      setIsProcessingPayment(false);
    }
  };

  // Update status display
  const updateStatusDisplay = () => {
    if (!paymentStatus) return null;
    
    const statusMessages = {
      checking: { message: 'Vérification du paiement...', type: 'info', icon: Clock },
      processing: { message: 'Paiement en cours de traitement...', type: 'info', icon: Clock },
      completed: { message: 'Paiement réussi!', type: 'success', icon: CheckCircle },
      cancelled: { message: 'Paiement annulé', type: 'warning', icon: AlertCircle },
      expired: { message: 'Session de paiement expirée', type: 'error', icon: AlertCircle },
      timeout: { message: 'Délai de vérification dépassé', type: 'error', icon: AlertCircle },
      error: { message: 'Erreur lors de la vérification', type: 'error', icon: AlertCircle }
    };
    
    const status = statusMessages[paymentStatus];
    if (!status) return null;
    
    const Icon = status.icon;
    
    return (
      <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        status.type === 'success' ? 'bg-green-800 text-green-100' :
        status.type === 'error' ? 'bg-red-800 text-red-100' :
        status.type === 'warning' ? 'bg-orange-800 text-orange-100' :
        'bg-blue-800 text-blue-100'
      }`}>
        <div className="flex items-center gap-2">
          <Icon className="w-5 h-5" />
          <span>{status.message}</span>
        </div>
      </div>
    );
  };

  // Fetch current prices
  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const response = await apiCall('/api/prices');
        const data = await response.json();
        setPrices(data);
      } catch (error) {
        console.error('Error fetching prices:', error);
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, 1000);
    return () => clearInterval(interval);
  }, [apiCall]);

  // Fetch current account details
  useEffect(() => {
    const fetchCurrentAccount = async () => {
      if (!user) return;
      
      try {
        const response = await apiCall(`/api/accounts/${accountType}`);
        const data = await response.json();
        setCurrentAccount(data);
      } catch (error) {
        console.error('Error fetching account details:', error);
      }
    };

    fetchCurrentAccount();
    const interval = setInterval(fetchCurrentAccount, 5000);
    return () => clearInterval(interval);
  }, [user, accountType, apiCall]);

  // Fetch positions
  useEffect(() => {
    const fetchPositions = async () => {
      if (!user) return;
      
      try {
        const response = await apiCall(`/api/positions/${accountType}`);
        const data = await response.json();
        setPositions(data);
      } catch (error) {
        console.error('Error fetching positions:', error);
      }
    };

    fetchPositions();
    const interval = setInterval(fetchPositions, 2000);
    return () => clearInterval(interval);
  }, [user, accountType, apiCall]);

  // Fetch trade history
  useEffect(() => {
    const fetchHistory = async () => {
      if (!user) return;
      
      try {
        const response = await apiCall(`/api/history/${accountType}`);
        const data = await response.json();
        setTradeHistory(data);
      } catch (error) {
        console.error('Error fetching trade history:', error);
      }
    };

    fetchHistory();
  }, [user, accountType, positions, apiCall]);

  // Fetch transactions
  useEffect(() => {
    const fetchTransactions = async () => {
      if (!user) return;
      
      try {
        const response = await apiCall(`/api/transactions/${accountType}`);
        const data = await response.json();
        setTransactions(data);
      } catch (error) {
        console.error('Error fetching transactions:', error);
      }
    };

    fetchTransactions();
  }, [user, accountType, currentAccount, apiCall]);

  const placeOrder = async () => {
    if (!user || !currentAccount) return;

    if (!orderForm.volume || orderForm.volume <= 0) {
      alert('Volume doit être supérieur à 0');
      return;
    }

    try {
      let leverage = 999999;
      if (orderForm.leverage !== 'unlimited') {
        leverage = parseInt(orderForm.leverage);
      }

      const orderData = {
        account_type: accountType,
        symbol: orderForm.symbol,
        order_type: orderForm.orderType,
        volume: parseFloat(orderForm.volume),
        leverage: leverage,
        timestamp: new Date().toISOString()
      };

      const response = await apiCall('/api/orders', {
        method: 'POST',
        body: JSON.stringify(orderData)
      });

      if (response.ok) {
        setOrderForm({
          symbol: 'EURUSD',
          orderType: 'buy',
          volume: 0.01,
          leverage: 'unlimited'
        });
      } else {
        const error = await response.json();
        alert(`Erreur: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Erreur lors du placement de l\'ordre');
    }
  };

  const closePosition = async (positionId) => {
    try {
      await apiCall(`/api/positions/${positionId}`, {
        method: 'DELETE'
      });
    } catch (error) {
      console.error('Error closing position:', error);
    }
  };

  // New Stripe deposit handler using emergentintegrations
  const handleStripeDeposit = async () => {
    if (!user || !transactionForm.amount) {
      alert('Veuillez entrer un montant');
      return;
    }

    if (parseFloat(transactionForm.amount) <= 0) {
      alert('Le montant doit être supérieur à 0');
      return;
    }

    try {
      const response = await apiCall('/api/stripe/checkout/session', {
        method: 'POST',
        body: JSON.stringify({
          account_type: accountType,
          amount: parseFloat(transactionForm.amount)
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Reset form and close dialog
        setTransactionForm({
          amount: '',
          description: ''
        });
        setIsTransactionOpen(false);
        
        if (accountType === 'demo') {
          // For demo accounts, show success and reload
          alert(`Dépôt démo de ${transactionForm.amount}€ effectué avec succès!`);
          setTimeout(() => window.location.reload(), 1000);
        } else {
          // For real accounts, redirect to Stripe Checkout
          window.location.href = data.url;
        }
      } else {
        const error = await response.json();
        alert(`Erreur: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error creating Stripe checkout:', error);
      alert('Erreur lors de la création du checkout Stripe');
    }
  };

  // Stripe withdrawal handler
  const handleStripeWithdrawal = async () => {
    if (!user || !withdrawalForm.amount) {
      alert('Veuillez entrer un montant');
      return;
    }

    if (parseFloat(withdrawalForm.amount) <= 0) {
      alert('Le montant doit être supérieur à 0');
      return;
    }

    try {
      const response = await apiCall('/api/stripe/withdrawal', {
        method: 'POST',
        body: JSON.stringify({
          account_type: accountType,
          amount: parseFloat(withdrawalForm.amount),
          description: withdrawalForm.description || 'Retrait de fonds'
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`${result.message}\nNouveau solde: ${result.new_balance}€`);
        setWithdrawalForm({
          amount: '',
          description: ''
        });
        setIsWithdrawalOpen(false);
      } else {
        const error = await response.json();
        alert(`Erreur: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error processing Stripe withdrawal:', error);
      alert('Erreur lors du retrait Stripe');
    }
  };

  const getCurrentPrice = (symbol) => {
    const price = prices.find(p => p.symbol === symbol);
    return price ? price : { bid: 0, ask: 0 };
  };

  const totalPL = positions.reduce((sum, pos) => sum + pos.profit_loss, 0);

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800">
      {/* Payment Status Display */}
      {updateStatusDisplay()}

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-12">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-4">
                ForexPro <span className="text-blue-400">Trader</span>
              </h1>
              <p className="text-lg text-gray-300 mb-6">
                Trading professionnel avec effet de levier illimité et spreads 0 pip
              </p>
              <div className="flex gap-6">
                <div className="flex items-center gap-2 text-green-400">
                  <Zap className="w-4 h-4" />
                  <span>Levier illimité</span>
                </div>
                <div className="flex items-center gap-2 text-blue-400">
                  <Shield className="w-4 h-4" />
                  <span>0 pip spread</span>
                </div>
                <div className="flex items-center gap-2 text-purple-400">
                  <CreditCard className="w-4 h-4" />
                  <span>Stripe sécurisé - 0% frais</span>
                </div>
              </div>
            </div>
            
            {/* User Profile Section */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-white font-medium">
                  {user?.profile?.first_name} {user?.profile?.last_name}
                </p>
                <p className="text-gray-400 text-sm">{user?.profile?.email}</p>
              </div>
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                {user?.profile?.first_name?.[0]}{user?.profile?.last_name?.[0]}
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleLogout}
                className="border-red-500 text-red-400 hover:bg-red-500/10"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Account Type Toggle & Balance */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <Tabs value={accountType} onValueChange={setAccountType} className="w-full max-w-md">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="demo">Compte Démo</TabsTrigger>
                <TabsTrigger value="real">Compte Réel</TabsTrigger>
              </TabsList>
            </Tabs>
            
            <div className="flex items-center gap-4">
              <div className="text-center">
                <div className="text-gray-400 text-sm">Balance</div>
                <div className="text-2xl font-bold text-white">
                  {currentAccount ? `${currentAccount.balance.toFixed(2)} €` : '0.00 €'}
                </div>
              </div>
              
              {/* Stripe Deposit Dialog */}
              <Dialog open={isTransactionOpen} onOpenChange={setIsTransactionOpen}>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    className="border-blue-500 text-blue-400 hover:bg-blue-500/10"
                    disabled={isProcessingPayment}
                  >
                    <CreditCard className="w-4 h-4 mr-2" />
                    Dépôt Stripe
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-gray-800 border-gray-700">
                  <DialogHeader>
                    <DialogTitle className="text-white">
                      Dépôt Stripe - Compte {accountType === 'demo' ? 'Démo' : 'Réel'}
                    </DialogTitle>
                    <DialogDescription className="text-gray-400">
                      {accountType === 'demo' 
                        ? 'Simulation de dépôt par carte de crédit (aucun paiement réel)'
                        : 'Dépôt sécurisé par carte de crédit via Stripe - 0% de frais'
                      }
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="amount" className="text-white">Montant (€)</Label>
                      <Input
                        id="amount"
                        type="number"
                        value={transactionForm.amount}
                        onChange={(e) => setTransactionForm({...transactionForm, amount: e.target.value})}
                        placeholder="100.00"
                        min="1"
                        step="0.01"
                        className="bg-gray-700 border-gray-600 text-white"
                      />
                    </div>
                    
                    <div className="border-t border-gray-700 pt-4">
                      <p className="text-sm text-gray-400 mb-3">
                        Montant: {transactionForm.amount || '0'}€ • Frais: 0€ • Total: {transactionForm.amount || '0'}€
                      </p>
                      <Button 
                        onClick={handleStripeDeposit}
                        disabled={!transactionForm.amount || parseFloat(transactionForm.amount) <= 0}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <CreditCard className="w-4 h-4 mr-2" />
                        {accountType === 'demo' ? 'Simuler le Dépôt' : 'Payer par Carte'}
                      </Button>
                      
                      {accountType === 'real' && (
                        <p className="text-xs text-gray-500 mt-2">
                          Vous serez redirigé vers Stripe pour saisir vos informations de carte sécurisées
                        </p>
                      )}
                    </div>
                  </div>
                </DialogContent>
              </Dialog>

              {/* Stripe Withdrawal Dialog */}
              <Dialog open={isWithdrawalOpen} onOpenChange={setIsWithdrawalOpen}>
                <DialogTrigger asChild>
                  <Button 
                    variant="outline" 
                    className="border-orange-500 text-orange-400 hover:bg-orange-500/10"
                    disabled={isProcessingPayment}
                  >
                    <Building2 className="w-4 h-4 mr-2" />
                    Retrait Stripe
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-gray-800 border-gray-700 max-w-md">
                  <DialogHeader>
                    <DialogTitle className="text-white">
                      Retrait Stripe - Compte {accountType === 'demo' ? 'Démo' : 'Réel'}
                    </DialogTitle>
                    <DialogDescription className="text-gray-400">
                      Retirez vos fonds via Stripe (virements sécurisés - 0% frais)
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="withdrawAmount" className="text-white">Montant (€)</Label>
                      <Input
                        id="withdrawAmount"
                        type="number"
                        value={withdrawalForm.amount}
                        onChange={(e) => setWithdrawalForm({...withdrawalForm, amount: e.target.value})}
                        placeholder="100.00"
                        min="1"
                        step="0.01"
                        className="bg-gray-700 border-gray-600 text-white"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="description" className="text-white">Description (optionnel)</Label>
                      <Input
                        id="description"
                        type="text"
                        value={withdrawalForm.description}
                        onChange={(e) => setWithdrawalForm({...withdrawalForm, description: e.target.value})}
                        placeholder="Retrait de fonds"
                        className="bg-gray-700 border-gray-600 text-white"
                      />
                    </div>
                    
                    <div className="border-t border-gray-700 pt-4">
                      <p className="text-sm text-gray-400 mb-3">
                        Montant: {withdrawalForm.amount || '0'}€ • Frais: 0€ • Net: {withdrawalForm.amount || '0'}€
                      </p>
                      <Button 
                        onClick={handleStripeWithdrawal} 
                        className="w-full bg-orange-600 hover:bg-orange-700 text-white"
                      >
                        <Building2 className="w-4 h-4 mr-2" />
                        Effectuer le Retrait Stripe
                      </Button>
                    </div>
                    
                    <p className="text-xs text-gray-500">
                      {accountType === 'demo' 
                        ? 'Retrait instantané simulé pour le compte démo'
                        : 'Retrait sécurisé par Stripe (1-3 jours ouvrables) - 0% frais'
                      }
                    </p>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Trading Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Price Feed */}
            <Card className="bg-gray-800/80 border-gray-700 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Cotations en Temps Réel
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Spreads 0 pip - Mise à jour chaque seconde
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {prices.map((price) => {
                  const isPositive = Math.random() > 0.5;
                  return (
                    <div key={price.symbol} className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        {price.symbol === 'EURUSD' ? (
                          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                            EUR
                          </div>
                        ) : (
                          <div className="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                            XAU
                          </div>
                        )}
                        <div>
                          <h3 className="text-white font-semibold">{price.symbol}</h3>
                          <p className="text-gray-400 text-sm">
                            {price.symbol === 'EURUSD' ? 'Euro / Dollar US' : 'Or / Dollar US'}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="text-gray-400 text-xs mb-1">BID</div>
                          <div className="text-white font-mono text-lg font-semibold">{price.bid}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-gray-400 text-xs mb-1">ASK</div>
                          <div className="text-white font-mono text-lg font-semibold">{price.ask}</div>
                        </div>
                        <div className="flex items-center">
                          {isPositive ? (
                            <TrendingUp className="w-5 h-5 text-green-400" />
                          ) : (
                            <TrendingDown className="w-5 h-5 text-red-400" />
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* Tabs for Positions, History and Transactions */}
            <Tabs defaultValue="positions" className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-gray-800/80 border-gray-700">
                <TabsTrigger value="positions" className="data-[state=active]:bg-gray-700">
                  Positions ({positions.length})
                </TabsTrigger>
                <TabsTrigger value="history" className="data-[state=active]:bg-gray-700">
                  <History className="w-4 h-4 mr-1" />
                  Historique
                </TabsTrigger>
                <TabsTrigger value="transactions" className="data-[state=active]:bg-gray-700">
                  <Wallet className="w-4 h-4 mr-1" />
                  Transactions
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="positions">
                <Card className="bg-gray-800/80 border-gray-700 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <DollarSign className="w-5 h-5" />
                        Positions Ouvertes
                      </span>
                      <div className="text-right">
                        <div className="text-sm text-gray-400">P&L Total</div>
                        <div className={`text-lg font-bold ${totalPL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {totalPL.toFixed(2)} €
                        </div>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {positions.length === 0 ? (
                      <p className="text-gray-400 text-center py-8">Aucune position ouverte</p>
                    ) : (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {positions.map((position) => (
                          <div key={position.position_id} className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant={position.order_type === 'buy' ? 'default' : 'secondary'}>
                                  {position.order_type.toUpperCase()}
                                </Badge>
                                <span className="text-white font-semibold">{position.symbol}</span>
                                <span className="text-gray-400">× {position.volume}</span>
                                <Badge variant="outline" className="text-xs text-yellow-400">
                                  {position.leverage === 999999 ? 'ILLIMITÉ' : `${position.leverage}×`}
                                </Badge>
                              </div>
                              <div className="text-sm text-gray-400 grid grid-cols-2 gap-4">
                                <div>Prix d'entrée: <span className="text-white">{position.open_price}</span></div>
                                <div>Prix actuel: <span className="text-white">{position.current_price}</span></div>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="text-right">
                                <div className={`text-xl font-bold ${position.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  {position.profit_loss >= 0 ? '+' : ''}{position.profit_loss.toFixed(2)} €
                                </div>
                                <div className="text-xs text-gray-400">P&L</div>
                              </div>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => closePosition(position.position_id)}
                                className="border-red-500 text-red-400 hover:bg-red-500/10"
                              >
                                Fermer
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="history">
                <Card className="bg-gray-800/80 border-gray-700 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white">Historique des Trades</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {tradeHistory.length === 0 ? (
                      <p className="text-gray-400 text-center py-8">Aucun trade terminé</p>
                    ) : (
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {tradeHistory.map((trade) => (
                          <div key={trade.position_id} className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg text-sm">
                            <div className="flex items-center gap-3">
                              <Badge variant={trade.order_type === 'buy' ? 'default' : 'secondary'} className="text-xs">
                                {trade.order_type.toUpperCase()}
                              </Badge>
                              <span className="text-white">{trade.symbol}</span>
                              <span className="text-gray-400">× {trade.volume}</span>
                            </div>
                            <div className="text-right">
                              <div className={`font-semibold ${trade.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {trade.profit_loss >= 0 ? '+' : ''}{trade.profit_loss?.toFixed(2) || '0.00'} €
                              </div>
                              <div className="text-xs text-gray-500">{trade.close_reason}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="transactions">
                <Card className="bg-gray-800/80 border-gray-700 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white">Historique des Transactions Stripe</CardTitle>
                    <CardDescription className="text-gray-400">
                      Dépôts et retraits sécurisés via Stripe - 0% frais
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {transactions.length === 0 ? (
                      <p className="text-gray-400 text-center py-8">Aucune transaction</p>
                    ) : (
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {transactions.map((transaction) => (
                          <div key={transaction.transaction_id} className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg">
                            <div className="flex items-center gap-3">
                              {transaction.transaction_type === 'stripe_deposit' ? (
                                <div className="w-6 h-6 bg-blue-500 rounded flex items-center justify-center">
                                  <CreditCard className="w-3 h-3 text-white" />
                                </div>
                              ) : transaction.transaction_type === 'stripe_withdrawal' ? (
                                <div className="w-6 h-6 bg-orange-500 rounded flex items-center justify-center">
                                  <Building2 className="w-3 h-3 text-white" />
                                </div>
                              ) : transaction.transaction_type === 'recharge' ? (
                                <Plus className="w-5 h-5 text-green-400" />
                              ) : (
                                <Wallet className="w-5 h-5 text-gray-400" />
                              )}
                              <div>
                                <div className="text-white font-medium">
                                  {transaction.transaction_type === 'stripe_deposit' ? 'Dépôt Stripe' :
                                   transaction.transaction_type === 'stripe_withdrawal' ? 'Retrait Stripe' :
                                   transaction.transaction_type === 'recharge' ? 'Recharge' : 'Transaction'}
                                </div>
                                <div className="text-gray-400 text-xs">
                                  {new Date(transaction.timestamp).toLocaleDateString('fr-FR', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })}
                                </div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className={`font-bold ${
                                transaction.transaction_type === 'stripe_deposit' || transaction.transaction_type === 'recharge'
                                  ? 'text-green-400' 
                                  : 'text-red-400'
                              }`}>
                                {transaction.transaction_type === 'stripe_deposit' || transaction.transaction_type === 'recharge' ? '+' : '-'}{transaction.amount.toFixed(2)} €
                              </div>
                              <div className={`text-xs ${
                                transaction.status === 'completed' ? 'text-green-500' :
                                transaction.status === 'processing' ? 'text-orange-500' :
                                transaction.status === 'pending' ? 'text-yellow-500' : 'text-gray-500'
                              }`}>
                                {transaction.status === 'completed' ? 'Complété' :
                                 transaction.status === 'processing' ? 'En cours' :
                                 transaction.status === 'pending' ? 'En attente' : transaction.status}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Trading Panel */}
          <div>
            <Card className="bg-gray-800/80 border-gray-700 backdrop-blur-sm sticky top-4">
              <CardHeader>
                <CardTitle className="text-white">Nouveau Trade</CardTitle>
                <CardDescription className="text-gray-400">
                  Compte {accountType === 'demo' ? 'Démo' : 'Réel'}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="symbol" className="text-white text-sm">Symbole</Label>
                    <Select value={orderForm.symbol} onValueChange={(value) => setOrderForm({...orderForm, symbol: value})}>
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-700 border-gray-600">
                        <SelectItem value="EURUSD">EUR/USD</SelectItem>
                        <SelectItem value="XAUUSD">XAU/USD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="orderType" className="text-white text-sm">Type</Label>
                    <Select value={orderForm.orderType} onValueChange={(value) => setOrderForm({...orderForm, orderType: value})}>
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-700 border-gray-600">
                        <SelectItem value="buy">BUY</SelectItem>
                        <SelectItem value="sell">SELL</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="volume" className="text-white text-sm">Volume</Label>
                    <Input
                      id="volume"
                      type="number"
                      value={orderForm.volume}
                      onChange={(e) => setOrderForm({...orderForm, volume: e.target.value})}
                      step="0.01"
                      min="0.01"
                      className="bg-gray-700 border-gray-600 text-white"
                    />
                  </div>

                  <div>
                    <Label htmlFor="leverage" className="text-white text-sm">Levier</Label>
                    <Select value={orderForm.leverage.toString()} onValueChange={(value) => setOrderForm({...orderForm, leverage: value})}>
                      <SelectTrigger className="bg-gray-700 border-gray-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-700 border-gray-600">
                        <SelectItem value="50">1:50</SelectItem>
                        <SelectItem value="100">1:100</SelectItem>
                        <SelectItem value="200">1:200</SelectItem>
                        <SelectItem value="500">1:500</SelectItem>
                        <SelectItem value="1000">1:1000</SelectItem>
                        <SelectItem value="unlimited">
                          <div className="flex items-center gap-2">
                            <Zap className="w-4 h-4 text-yellow-400" />
                            ILLIMITÉ
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-700">
                  <div className="text-sm text-gray-400 mb-3 flex justify-between">
                    <span>Prix: {getCurrentPrice(orderForm.symbol)[orderForm.orderType === 'buy' ? 'ask' : 'bid']}</span>
                    <span className="text-yellow-400">
                      {orderForm.leverage === 'unlimited' ? '∞ Levier' : `${orderForm.leverage}× Levier`}
                    </span>
                  </div>
                  <Button 
                    onClick={placeOrder}
                    className={`w-full font-bold py-3 ${orderForm.orderType === 'buy' 
                      ? 'bg-green-600 hover:bg-green-700 buy-button' 
                      : 'bg-red-600 hover:bg-red-700 sell-button'
                    } text-white`}
                  >
                    {orderForm.orderType === 'buy' ? 'ACHETER' : 'VENDRE'} {orderForm.symbol}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingDashboard;
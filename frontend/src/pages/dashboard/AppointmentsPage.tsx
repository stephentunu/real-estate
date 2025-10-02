
import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Clock, MapPin, Phone, User, Check, X, ChevronRight, Filter, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import DashboardLayout from '@/components/DashboardLayout';
import { useToast } from '@/hooks/use-toast';
import { Link } from 'react-router-dom';
import { appointmentService, Appointment } from '@/services/appointmentService';
import { handleAPIError } from '@/services/errorHandler';

const AppointmentsPage = () => {
  const { toast } = useToast();
  
  // State management
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch appointments on component mount
  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await appointmentService.getUserAppointments();
        setAppointments(data);
      } catch (err) {
        setError('Failed to load appointments. Please try again.');
        handleAPIError(err, 'Loading appointments');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const handleCancelAppointment = async (id: number) => {
    try {
      await appointmentService.cancelAppointment(id);
      setAppointments(appointments.map(appointment => 
        appointment.id === id ? {...appointment, status: 'cancelled' as const} : appointment
      ));
      toast({
        title: "Appointment cancelled",
        description: "The appointment has been cancelled successfully.",
      });
    } catch (error) {
      handleAPIError(error, 'Cancelling appointment');
    }
  };

  const handleConfirmAppointment = async (id: number) => {
    try {
      await appointmentService.confirmAppointment(id);
      setAppointments(appointments.map(appointment => 
        appointment.id === id ? {...appointment, status: 'confirmed' as const} : appointment
      ));
      toast({
        title: "Appointment confirmed",
        description: "The appointment has been confirmed successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to confirm appointment. Please try again.",
        variant: "destructive"
      });
    }
  };

  const filterAppointments = (status: string) => {
    return appointments.filter(appointment => appointment.status === status);
  };

  // Function to format date
  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      weekday: 'long'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
  };

  // Loading state
  if (isLoading) {
    return (
      <DashboardLayout title="My Appointments">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading appointments...</span>
        </div>
      </DashboardLayout>
    );
  }

  // Error state
  if (error) {
    return (
      <DashboardLayout title="My Appointments">
        <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
          <X className="h-12 w-12 mx-auto text-red-500" />
          <h3 className="mt-4 text-lg font-medium">Error Loading Appointments</h3>
          <p className="mt-2 text-rental-600 dark:text-rental-400">{error}</p>
          <Button 
            className="mt-4" 
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="My Appointments">
      <Tabs defaultValue="upcoming">
        <TabsList className="mb-4">
          <TabsTrigger value="upcoming">
            Upcoming ({filterAppointments('confirmed').length + filterAppointments('pending').length})
          </TabsTrigger>
          <TabsTrigger value="completed">
            Completed ({filterAppointments('completed').length})
          </TabsTrigger>
          <TabsTrigger value="cancelled">
            Cancelled ({filterAppointments('cancelled').length})
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="upcoming">
          {filterAppointments('confirmed').length === 0 && filterAppointments('pending').length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
              <CalendarIcon className="h-12 w-12 mx-auto text-rental-400" />
              <h3 className="mt-4 text-lg font-medium">No upcoming appointments</h3>
              <p className="mt-2 text-rental-600 dark:text-rental-400">
                You don't have any confirmed or pending property viewings. Browse properties to schedule viewings.
              </p>
              <Button className="mt-4" asChild>
                <Link to="/properties">
                  Browse Properties
                </Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {[...filterAppointments('confirmed'), ...filterAppointments('pending')]
                .sort((a, b) => new Date(a.scheduled_date).getTime() - new Date(b.scheduled_date).getTime())
                .map((appointment) => (
                  <Card key={appointment.id} className="overflow-hidden">
                    <CardContent className="p-0">
                      <div className="flex flex-col sm:flex-row">
                        <div className="sm:w-48 h-48">
                          {appointment.property?.primary_image ? (
                            <img 
                              src={appointment.property.primary_image} 
                              alt={appointment.property.title} 
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full bg-rental-100 dark:bg-rental-800 flex items-center justify-center rounded-l-lg">
                              <CalendarIcon className="h-12 w-12 text-rental-400" />
                            </div>
                          )}
                        </div>
                        <div className="p-4 flex-grow">
                          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div>
                              <h3 className="text-lg font-semibold">{appointment.title}</h3>
                              {appointment.property && (
                                <p className="text-sm text-rental-600 dark:text-rental-400 flex items-center">
                                  <MapPin className="h-4 w-4 mr-1" />
                                  {appointment.property.address}, {appointment.property.city}, {appointment.property.state}
                                </p>
                              )}
                            </div>
                            <Badge
                              className={
                                appointment.status === 'confirmed' ? "bg-green-100 text-green-800 hover:bg-green-100" :
                                "bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
                              }
                            >
                              {appointment.status === 'confirmed' ? "Confirmed" : "Pending"}
                            </Badge>
                          </div>
                          
                          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm text-rental-600 dark:text-rental-400">Date & Time</p>
                              <p className="font-medium flex items-center mt-1">
                                <CalendarIcon className="h-4 w-4 mr-1 text-rental-500" />
                                {formatDate(appointment.scheduled_date)}
                              </p>
                              <p className="font-medium flex items-center mt-1">
                                <Clock className="h-4 w-4 mr-1 text-rental-500" />
                                {appointment.scheduled_time}
                              </p>
                            </div>
                            {appointment.agent && (
                              <div>
                                <p className="text-sm text-rental-600 dark:text-rental-400">Agent</p>
                                <p className="font-medium flex items-center mt-1">
                                  <User className="h-4 w-4 mr-1 text-rental-500" />
                                  {appointment.agent.first_name} {appointment.agent.last_name}
                                </p>
                                {appointment.agent.phone && (
                                  <p className="font-medium flex items-center mt-1">
                                    <Phone className="h-4 w-4 mr-1 text-rental-500" />
                                    {appointment.agent.phone}
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                          
                          {(appointment.description || appointment.client_notes || appointment.agent_notes) && (
                            <div className="mt-3 text-sm">
                              <p className="text-rental-600 dark:text-rental-400">Notes:</p>
                              {appointment.description && <p>{appointment.description}</p>}
                              {appointment.client_notes && <p><strong>Client:</strong> {appointment.client_notes}</p>}
                              {appointment.agent_notes && <p><strong>Agent:</strong> {appointment.agent_notes}</p>}
                            </div>
                          )}
                          
                          <div className="mt-4 flex flex-wrap gap-2">
                            {appointment.property && (
                              <Button size="sm" asChild>
                                <Link to={`/properties/${appointment.property.id}`}>
                                  View Property
                                </Link>
                              </Button>
                            )}
                            {appointment.status === 'pending' && (
                              <Button 
                                size="sm" 
                                variant="outline"
                                className="text-green-600"
                                onClick={() => handleConfirmAppointment(appointment.id)}
                              >
                                <Check className="h-4 w-4 mr-1" />
                                Confirm
                              </Button>
                            )}
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleCancelAppointment(appointment.id)}
                            >
                              <X className="h-4 w-4 mr-1" />
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="completed">
          {filterAppointments('completed').length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
              <Check className="h-12 w-12 mx-auto text-rental-400" />
              <h3 className="mt-4 text-lg font-medium">No completed appointments</h3>
              <p className="mt-2 text-rental-600 dark:text-rental-400">
                You don't have any completed property viewings yet.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filterAppointments('completed').map((appointment) => (
                <Card key={appointment.id} className="overflow-hidden">
                  <CardContent className="p-4">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <h3 className="text-lg font-semibold">{appointment.title}</h3>
                        {appointment.property && (
                          <p className="text-sm text-rental-600 dark:text-rental-400 flex items-center">
                            <MapPin className="h-4 w-4 mr-1" />
                            {appointment.property.address}, {appointment.property.city}, {appointment.property.state}
                          </p>
                        )}
                        <div className="flex items-center mt-1">
                          <CalendarIcon className="h-4 w-4 mr-1 text-rental-500" />
                          <p className="text-sm text-rental-600 dark:text-rental-400">
                            {formatDate(appointment.scheduled_date)} at {appointment.scheduled_time}
                          </p>
                        </div>
                      </div>
                      {appointment.property && (
                        <Button size="sm" variant="outline" asChild className="mt-3 sm:mt-0">
                          <Link to={`/properties/${appointment.property.id}`}>
                            View Property
                            <ChevronRight className="h-4 w-4 ml-1" />
                          </Link>
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="cancelled">
          {filterAppointments('cancelled').length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
              <X className="h-12 w-12 mx-auto text-rental-400" />
              <h3 className="mt-4 text-lg font-medium">No cancelled appointments</h3>
              <p className="mt-2 text-rental-600 dark:text-rental-400">
                You don't have any cancelled property viewings.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filterAppointments('cancelled').map((appointment) => (
                <Card key={appointment.id} className="overflow-hidden">
                  <CardContent className="p-4">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <h3 className="text-lg font-semibold">{appointment.title}</h3>
                        {appointment.property && (
                          <p className="text-sm text-rental-600 dark:text-rental-400 flex items-center">
                            <MapPin className="h-4 w-4 mr-1" />
                            {appointment.property.address}, {appointment.property.city}, {appointment.property.state}
                          </p>
                        )}
                        <div className="flex items-center mt-1">
                          <CalendarIcon className="h-4 w-4 mr-1 text-rental-500" />
                          <p className="text-sm text-rental-600 dark:text-rental-400">
                            {formatDate(appointment.scheduled_date)} at {appointment.scheduled_time}
                          </p>
                        </div>
                        {appointment.cancellation_reason && (
                          <p className="mt-2 text-sm text-rental-600 dark:text-rental-400 italic">
                            Reason: {appointment.cancellation_reason}
                          </p>
                        )}
                      </div>
                      {appointment.property && (
                         <Button size="sm" asChild className="mt-3 sm:mt-0">
                           <Link to={`/properties/${appointment.property.id}`}>
                            Reschedule
                           </Link>
                         </Button>
                       )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </DashboardLayout>
  );
};

export default AppointmentsPage;

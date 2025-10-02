
import React, { useState } from 'react';
import { Upload, MapPin, Home, DollarSign, Bed, Bath, Square, Plus, Trash, ChevronRight, ChevronLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import Layout from '@/components/Layout';
import { useToast } from '@/hooks/use-toast';

const ListPropertyPage = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    address: '',
    price: '',
    beds: '',
    baths: '',
    area: '',
    type: 'apartment',
  });
  const [images, setImages] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const totalSteps = 3;
  const progress = (currentStep / totalSteps) * 100;

  const steps = [
    { title: 'Basic Information', description: 'Property title, price, and address' },
    { title: 'Property Details', description: 'Type, bedrooms, bathrooms, and area' },
    { title: 'Images & Finish', description: 'Upload photos and complete listing' }
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileArray = Array.from(e.target.files);
      setImages([...images, ...fileArray]);
    }
  };

  const removeImage = (index: number) => {
    setImages(images.filter((_, i) => i !== index));
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.title && formData.price && formData.address && formData.description;
      case 2:
        return formData.type && formData.beds && formData.baths && formData.area;
      case 3:
        return images.length > 0;
      default:
        return false;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate form submission
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Success!",
        description: "Your property has been listed successfully.",
      });
    }, 2000);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card>
            <CardContent className="pt-6">
              <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="title">Property Title</label>
                  <div className="relative">
                    <Home className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="title"
                      name="title"
                      placeholder="e.g. Modern Apartment in Westlands" 
                      className="pl-10" 
                      value={formData.title}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="price">Monthly Rent (KSh)</label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="price"
                      name="price"
                      type="number" 
                      placeholder="e.g. 75000" 
                      className="pl-10" 
                      value={formData.price}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium" htmlFor="address">Address</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="address"
                      name="address"
                      placeholder="e.g. Westlands, Nairobi, Kenya" 
                      className="pl-10" 
                      value={formData.address}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium" htmlFor="description">Description</label>
                  <textarea 
                    id="description"
                    name="description"
                    placeholder="Describe your property" 
                    className="w-full px-3 py-2 text-base rounded-md border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm min-h-[120px]" 
                    value={formData.description}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 2:
        return (
          <Card>
            <CardContent className="pt-6">
              <h2 className="text-xl font-semibold mb-4">Property Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="type">Property Type</label>
                  <select 
                    id="type"
                    name="type"
                    className="w-full px-3 py-2 text-base rounded-md border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm h-10" 
                    value={formData.type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="townhouse">Townhouse</option>
                    <option value="villa">Villa</option>
                    <option value="office">Office Space</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="beds">Bedrooms</label>
                  <div className="relative">
                    <Bed className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="beds"
                      name="beds"
                      type="number" 
                      placeholder="e.g. 2" 
                      className="pl-10" 
                      value={formData.beds}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="baths">Bathrooms</label>
                  <div className="relative">
                    <Bath className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="baths"
                      name="baths"
                      type="number" 
                      placeholder="e.g. 2" 
                      className="pl-10" 
                      value={formData.baths}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="area">Area (sq ft)</label>
                  <div className="relative">
                    <Square className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      id="area"
                      name="area"
                      type="number" 
                      placeholder="e.g. 1200" 
                      className="pl-10" 
                      value={formData.area}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );

      case 3:
        return (
          <Card>
            <CardContent className="pt-6">
              <h2 className="text-xl font-semibold mb-4">Property Images</h2>
              <div className="border-2 border-dashed border-muted-foreground/20 rounded-lg p-6 text-center">
                <input
                  type="file"
                  id="images"
                  multiple
                  accept="image/*"
                  className="hidden"
                  onChange={handleImageUpload}
                />
                <label htmlFor="images" className="cursor-pointer">
                  <Upload className="h-10 w-10 mx-auto mb-2 text-muted-foreground" />
                  <p className="text-muted-foreground mb-1">Drag and drop images here or click to browse</p>
                  <p className="text-xs text-muted-foreground/70">PNG, JPG, GIF up to 5MB</p>
                </label>
              </div>

              {images.length > 0 && (
                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
                  {images.map((image, index) => (
                    <div key={index} className="relative group">
                      <img 
                        src={URL.createObjectURL(image)} 
                        alt={`Property ${index}`} 
                        className="w-full h-24 object-cover rounded-md"
                      />
                      <button
                        type="button"
                        className="absolute top-1 right-1 bg-background rounded-full p-1 shadow opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeImage(index)}
                      >
                        <Trash className="h-3 w-3 text-destructive" />
                      </button>
                    </div>
                  ))}
                  <label 
                    htmlFor="images"
                    className="border-2 border-dashed border-muted-foreground/20 rounded-md h-24 flex items-center justify-center cursor-pointer"
                  >
                    <Plus className="h-5 w-5 text-muted-foreground" />
                  </label>
                </div>
              )}
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <Layout>
      <div className="pt-28 pb-16 min-h-screen">
        <div className="container px-4 md:px-6 max-w-4xl">
          <h1 className="text-3xl font-bold mb-2">List Your Property</h1>
          <p className="text-muted-foreground mb-8">
            Complete the form below to list your property on Jaston
          </p>

          {/* Progress Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium">Step {currentStep} of {totalSteps}</h2>
              <span className="text-sm text-muted-foreground">{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="mb-4" />
            
            <div className="grid grid-cols-3 gap-4">
              {steps.map((step, index) => (
                <div 
                  key={index}
                  className={`text-center p-3 rounded-lg border ${
                    index + 1 === currentStep 
                      ? 'border-primary bg-primary/5' 
                      : index + 1 < currentStep 
                        ? 'border-green-500 bg-green-50 dark:bg-green-950' 
                        : 'border-muted bg-muted/20'
                  }`}
                >
                  <div className={`text-sm font-medium mb-1 ${
                    index + 1 === currentStep 
                      ? 'text-primary' 
                      : index + 1 < currentStep 
                        ? 'text-green-600 dark:text-green-400' 
                        : 'text-muted-foreground'
                  }`}>
                    {step.title}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {step.description}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-8">
            {renderStepContent()}

            {/* Navigation Buttons */}
            <div className="flex justify-between">
              <Button 
                type="button" 
                variant="outline" 
                onClick={prevStep}
                disabled={currentStep === 1}
                className="flex items-center gap-2"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>

              {currentStep < totalSteps ? (
                <Button 
                  type="button" 
                  onClick={nextStep}
                  disabled={!isStepValid()}
                  className="flex items-center gap-2"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              ) : (
                <Button 
                  type="submit" 
                  disabled={isLoading || !isStepValid()}
                  className="px-8"
                >
                  {isLoading ? "Submitting..." : "List Property"}
                </Button>
              )}
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};

export default ListPropertyPage;

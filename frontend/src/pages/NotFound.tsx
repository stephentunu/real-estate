
import React from "react";
import { Link, useLocation } from "react-router-dom";
import { ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import Layout from "@/components/Layout";

const NotFound = () => {
  const location = useLocation();

  return (
    <Layout>
      <div className="min-h-screen flex items-center justify-center px-4 py-20">
        <div className="text-center max-w-xl animate-fade-up">
          <div className="mb-8">
            <span className="inline-block text-8xl font-bold text-primary">404</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-rental-900 dark:text-white mb-4">
            Page Not Found
          </h1>
          <p className="text-rental-600 dark:text-rental-400 text-lg mb-8">
            We couldn't find the page you're looking for. The page may have been moved, deleted, or never existed.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild variant="default" className="bg-primary hover:bg-primary/90 text-white">
              <Link to="/">
                <Home className="mr-2 h-4 w-4" />
                Back to Home
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/" onClick={() => window.history.back()}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Back
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default NotFound;

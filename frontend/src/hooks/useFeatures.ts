import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { featureService, Feature, UserFeatureAccess } from '@/services/featureService';

export const useFeatures = () => {
  const { user, profile } = useAuth();
  const [features, setFeatures] = useState<Feature[]>([]);
  const [userFeatures, setUserFeatures] = useState<UserFeatureAccess[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && profile) {
      fetchFeatures();
      fetchUserFeatures();
    }
  }, [user, profile, fetchUserFeatures]);

  const fetchFeatures = async () => {
    try {
      const data = await featureService.getFeatures();
      setFeatures(data);
    } catch (error) {
      console.error('Error fetching features:', error);
    }
  };

  const fetchUserFeatures = useCallback(async () => {
    if (!user) return;

    try {
      const data = await featureService.getUserFeatures();
      setUserFeatures(data || []);
    } catch (error) {
      console.error('Error fetching user features:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  const enableFeature = async (featureId: number, configuration: Record<string, unknown> = {}) => {
    if (!user) return;

    try {
      await featureService.updateUserFeature(featureId, {
        is_enabled: true,
        configuration
      });

      await fetchUserFeatures();
    } catch (error) {
      console.error('Error enabling feature:', error);
      throw error;
    }
  };

  const disableFeature = async (featureId: number) => {
    if (!user) return;

    try {
      await featureService.updateUserFeature(featureId, {
        is_enabled: false
      });

      await fetchUserFeatures();
    } catch (error) {
      console.error('Error disabling feature:', error);
      throw error;
    }
  };

  const hasFeature = (featureName: string): boolean => {
    const feature = features.find(f => f.name === featureName);
    if (!feature) return false;

    const userFeature = userFeatures.find(uf => uf.feature.id === feature.id);
    return userFeature?.is_enabled ?? true; // Default to enabled if not explicitly disabled
  };

  const getFeatureConfig = (featureName: string): Record<string, unknown> => {
    const feature = features.find(f => f.name === featureName);
    if (!feature) return {};

    const userFeature = userFeatures.find(uf => uf.feature.id === feature.id);
    return {
      ...feature.configuration,
      ...userFeature?.configuration
    };
  };

  const availableFeatures = features.filter(feature => 
    feature.user_roles.includes(profile?.user_role || 'buyer')
  );

  const enabledFeatures = features.filter(feature => hasFeature(feature.name));

  return {
    features: availableFeatures,
    userFeatures,
    enabledFeatures,
    loading,
    enableFeature,
    disableFeature,
    hasFeature,
    getFeatureConfig
  };
};

import React, { useState, useEffect } from 'react';
import { Calendar, User, ArrowRight, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import Layout from '@/components/Layout';
import { blogService, BlogPostListItem, BlogCategory } from '@/services/blogService';
import { handleAPIError } from '@/services/errorHandler';

const BlogPage = () => {
  const [activeCategory, setActiveCategory] = useState('All');
  const [blogPosts, setBlogPosts] = useState<BlogPostListItem[]>([]);
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBlogData();
  }, []);

  const fetchBlogData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch blog posts and categories in parallel
      const [postsResponse, categoriesResponse] = await Promise.all([
        blogService.getBlogPosts({ status: 'published', ordering: '-published_at' }),
        blogService.getBlogCategories()
      ]);
      
      setBlogPosts(postsResponse.results);
      setCategories(categoriesResponse);
    } catch (err) {
      handleAPIError(err, 'Loading blog posts');
      setError('Failed to load blog posts');
      // Fallback to empty arrays on error
      setBlogPosts([]);
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    fetchBlogData();
  };
  
  const handleCategoryChange = (category: string) => {
    setActiveCategory(category);
  };

  const filteredPosts = activeCategory === 'All' 
    ? blogPosts 
    : blogPosts.filter(post => post.category?.name === activeCategory);

  if (loading) {
    return (
      <Layout>
        <div className="pt-24 pb-16 min-h-screen">
          <div className="container px-4 md:px-6">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
                <p className="text-rental-600 dark:text-rental-400">Loading blog posts...</p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="pt-24 pb-16 min-h-screen">
          <div className="container px-4 md:px-6">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="text-center">
                <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
                <Button onClick={handleRetry} variant="outline">
                  Try Again
                </Button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-10">
            <div>
              <h1 className="text-3xl font-bold mb-2">Jaston Blog</h1>
              <p className="text-rental-600 dark:text-rental-400">
                Insights and guides on Kenyan real estate
              </p>
            </div>
            <div className="mt-4 md:mt-0">
              <div className="flex overflow-x-auto py-2 space-x-2">
                <Button 
                  key="all" 
                  variant={activeCategory === 'All' ? 'default' : 'outline'} 
                  size="sm"
                  onClick={() => handleCategoryChange('All')}
                >
                  All
                </Button>
                {categories.map((category) => (
                  <Button 
                    key={category.id} 
                    variant={category.name === activeCategory ? 'default' : 'outline'} 
                    size="sm"
                    onClick={() => handleCategoryChange(category.name)}
                  >
                    {category.name}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {filteredPosts.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-rental-600 dark:text-rental-400">
                No blog posts found{activeCategory !== 'All' ? ` in "${activeCategory}" category` : ''}.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredPosts.map((post) => (
              <div key={post.id} className="bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                <div className="aspect-video overflow-hidden">
                  <img 
                    src={post.featured_image || 'https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&w=1000'} 
                    alt={post.title} 
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center text-sm text-rental-500 dark:text-rental-400 mb-2">
                    <span className="px-2 py-1 bg-primary/10 text-primary rounded-full text-xs">
                      {post.category?.name || 'Uncategorized'}
                    </span>
                    <span className="mx-2">•</span>
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {new Date(post.published_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </div>
                  </div>
                  <h2 className="text-xl font-semibold mb-2 line-clamp-2">
                    {post.title}
                  </h2>
                  <p className="text-rental-600 dark:text-rental-400 mb-4 line-clamp-3">
                    {post.excerpt}
                  </p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <User className="w-4 h-4 mr-1 text-rental-500 dark:text-rental-400" />
                      <span className="text-sm text-rental-500 dark:text-rental-400">
                        {post.author ? `${post.author.first_name} ${post.author.last_name}`.trim() || post.author.username : 'Anonymous'}
                      </span>
                    </div>
                    <Button asChild variant="ghost" size="sm" className="text-primary">
                      <Link to={`/blog/${post.id}`}>
                        Read More
                        <ArrowRight size={16} className="ml-1" />
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
              ))}
            </div>
          )}

          <div className="mt-12 flex justify-center">
            <Button variant="outline" className="mr-2">
              Previous
            </Button>
            <Button>
              Next
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default BlogPage;

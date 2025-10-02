/**
 * Blog Service - Tightly coupled with Django REST API backend
 * Uses unified API client for consistent request handling
 */

import apiClient, { PaginatedResponse } from './apiClient';

// Type definitions matching backend models
export interface BlogCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  color?: string;
  posts_count: number;
  is_visible: boolean;
  created_at: string;
  updated_at: string;
}

export interface BlogAuthor {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email?: string;
  avatar?: string;
}

export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  featured_image?: string;
  category: BlogCategory;
  author: BlogAuthor;
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  tags: string[];
  views_count: number;
  read_time: number;
  published_at?: string;
  created_at: string;
  updated_at: string;
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string;
}

export interface BlogPostListItem {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  featured_image?: string;
  category: BlogCategory;
  author: BlogAuthor;
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  tags: string[];
  views_count: number;
  read_time: number;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BlogFilters {
  category?: number;
  status?: 'draft' | 'published' | 'archived';
  is_featured?: boolean;
  author?: number;
  search?: string;
  ordering?: string;
  page?: number;
  limit?: number;
}

export interface BlogComment {
  id: number;
  post: number;
  author: BlogAuthor;
  content: string;
  status: 'pending' | 'approved' | 'rejected';
  parent?: number;
  replies?: BlogComment[];
  created_at: string;
  updated_at: string;
}

export interface CreateBlogCommentData {
  post: number;
  content: string;
  parent?: number;
}

export interface UpdateBlogPostData {
  title?: string;
  content?: string;
  excerpt?: string;
  category?: number;
  tags?: string[];
  status?: 'draft' | 'published' | 'archived';
  is_featured?: boolean;
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string;
}

export interface CreateBlogPostData {
  title: string;
  content: string;
  excerpt: string;
  category: number;
  tags?: string[];
  featured_image?: File;
  status?: 'draft' | 'published' | 'archived';
  is_featured?: boolean;
  seo_title?: string;
  seo_description?: string;
  seo_keywords?: string;
}

/**
 * Blog service methods
 */
export const blogService = {
  /**
   * Get blog posts with optional filters
   */
  async getBlogPosts(filters?: BlogFilters): Promise<PaginatedResponse<BlogPostListItem>> {
    return apiClient.get('/blog/posts/', { params: filters });
  },

  /**
   * Get a single blog post by ID or slug
   */
  async getBlogPost(identifier: string | number): Promise<BlogPost> {
    const endpoint = typeof identifier === 'number' ? `/blog/posts/${identifier}/` : `/blog/posts/slug/${identifier}/`;
    return apiClient.get(endpoint);
  },

  /**
   * Get featured blog posts
   */
  async getFeaturedBlogPosts(limit?: number): Promise<BlogPostListItem[]> {
    return apiClient.get('/blog/posts/featured/', { params: { limit } });
  },

  /**
   * Get recent blog posts
   */
  async getRecentBlogPosts(limit?: number): Promise<BlogPostListItem[]> {
    return apiClient.get('/blog/posts/recent/', { params: { limit } });
  },

  /**
   * Get popular blog posts
   */
  async getPopularBlogPosts(limit?: number): Promise<BlogPostListItem[]> {
    return apiClient.get('/blog/posts/popular/', { params: { limit } });
  },

  /**
   * Get blog statistics
   */
  async getBlogStats(): Promise<{
    total_posts: number;
    published_posts: number;
    draft_posts: number;
    total_views: number;
    total_comments: number;
  }> {
    return apiClient.get('/blog/posts/stats/');
  },

  /**
   * Create new blog post
   */
  async createBlogPost(data: CreateBlogPostData): Promise<BlogPost> {
    const formData = new FormData();
    
    // Append all data to form data for file upload support
    Object.entries(data).forEach(([key, value]) => {
      if (key === 'featured_image' && value instanceof File) {
        formData.append(key, value);
      } else if (Array.isArray(value)) {
        value.forEach(v => formData.append(key, v));
      } else if (value !== undefined) {
        formData.append(key, value.toString());
      }
    });

    return apiClient.post('/blog/posts/', formData, {
      headers: {
        'Content-Type': undefined, // Let browser set content-type
      },
    });
  },

  /**
   * Update blog post
   */
  async updateBlogPost(id: number, data: UpdateBlogPostData): Promise<BlogPost> {
    return apiClient.patch(`/blog/posts/${id}/`, data);
  },

  /**
   * Delete blog post
   */
  async deleteBlogPost(id: number): Promise<void> {
    return apiClient.delete(`/blog/posts/${id}/`);
  },

  /**
   * Get blog categories
   */
  async getCategories(): Promise<BlogCategory[]> {
    return apiClient.get('/blog/categories/');
  },

  /**
   * Get specific category
   */
  async getCategory(id: number): Promise<BlogCategory> {
    return apiClient.get(`/blog/categories/${id}/`);
  },

  /**
   * Get posts in a specific category
   */
  async getPostsByCategory(categoryId: number, params?: {
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<BlogPostListItem>> {
    return apiClient.get(`/blog/categories/${categoryId}/posts/`, { params });
  },

  /**
   * Get blog comments for a post
   */
  async getComments(postId: number, params?: {
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<BlogComment>> {
    return apiClient.get('/blog/comments/', { params: { post: postId, ...params } });
  },

  /**
   * Create new comment
   */
  async createComment(data: CreateBlogCommentData): Promise<BlogComment> {
    return apiClient.post('/blog/comments/', data);
  },

  /**
   * Update comment
   */
  async updateComment(id: number, content: string): Promise<BlogComment> {
    return apiClient.patch(`/blog/comments/${id}/`, { content });
  },

  /**
   * Delete comment
   */
  async deleteComment(id: number): Promise<void> {
    return apiClient.delete(`/blog/comments/${id}/`);
  },

  /**
   * Approve comment (admin/moderator only)
   */
  async approveComment(id: number): Promise<BlogComment> {
    return apiClient.post(`/blog/comments/${id}/approve/`, {});
  },

  /**
   * Reject comment (admin/moderator only)
   */
  async rejectComment(id: number): Promise<BlogComment> {
    return apiClient.post(`/blog/comments/${id}/reject/`, {});
  },

  /**
   * Search blog posts
   */
  async searchPosts(query: string, filters?: Omit<BlogFilters, 'search'>): Promise<PaginatedResponse<BlogPostListItem>> {
    return this.getBlogPosts({ search: query, ...filters });
  },

  /**
   * Get posts by author
   */
  async getPostsByAuthor(authorId: number, params?: Omit<BlogFilters, 'author'>): Promise<PaginatedResponse<BlogPostListItem>> {
    return this.getBlogPosts({ author: authorId, ...params });
  },

  /**
   * Get related posts
   */
  async getRelatedPosts(postId: number, limit: number = 5): Promise<BlogPostListItem[]> {
    return apiClient.get(`/blog/posts/${postId}/related/`, { params: { limit } });
  },

  /**
   * Increment post view count
   */
  async incrementViewCount(postId: number): Promise<void> {
    return apiClient.post(`/blog/posts/${postId}/view/`, {});
  },
};

/**
 * Blog category service methods
 */
export const blogCategoryService = {
  /**
   * Get all categories
   */
  async getCategories(): Promise<BlogCategory[]> {
    return apiClient.get('/blog/categories/');
  },

  /**
   * Get category by ID
   */
  async getCategory(id: number): Promise<BlogCategory> {
    return apiClient.get(`/blog/categories/${id}/`);
  },

  /**
   * Create new category
   */
  async createCategory(data: {
    name: string;
    description?: string;
    color?: string;
  }): Promise<BlogCategory> {
    return apiClient.post('/blog/categories/', data);
  },

  /**
   * Update category
   */
  async updateCategory(id: number, data: {
    name?: string;
    description?: string;
    color?: string;
  }): Promise<BlogCategory> {
    return apiClient.patch(`/blog/categories/${id}/`, data);
  },

  /**
   * Delete category
   */
  async deleteCategory(id: number): Promise<void> {
    return apiClient.delete(`/blog/categories/${id}/`);
  },
};

export default blogService;
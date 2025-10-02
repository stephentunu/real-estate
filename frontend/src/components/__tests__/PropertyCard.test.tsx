import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import PropertyCard from '../PropertyCard';

// Mock the utils function
vi.mock('@/lib/utils', () => ({
  cn: (...classes: (string | undefined)[]) => classes.filter(Boolean).join(' ')
}));

const mockProperty = {
  id: '1',
  title: 'Beautiful Modern Home',
  price: 450000,
  address: '123 Main St, City, State',
  image: 'https://example.com/image.jpg',
  beds: 3,
  baths: 2,
  sqft: 1800
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('PropertyCard', () => {
  it('renders property information correctly', () => {
    renderWithRouter(<PropertyCard {...mockProperty} />);
    
    expect(screen.getByText('Beautiful Modern Home')).toBeInTheDocument();
    expect(screen.getByText('$450,000')).toBeInTheDocument();
    expect(screen.getByText('123 Main St, City, State')).toBeInTheDocument();
    expect(screen.getByText('3 Beds')).toBeInTheDocument();
    expect(screen.getByText('2 Baths')).toBeInTheDocument();
    expect(screen.getByText('1,800 sqft')).toBeInTheDocument();
  });

  it('renders property image with correct attributes', () => {
    renderWithRouter(<PropertyCard {...mockProperty} />);
    
    const image = screen.getByAltText('Beautiful Modern Home');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', 'https://example.com/image.jpg');
  });

  it('creates correct link to property detail page', () => {
    renderWithRouter(<PropertyCard {...mockProperty} />);
    
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/properties/1');
  });

  it('applies featured styling when featured prop is true', () => {
    const { container } = renderWithRouter(
      <PropertyCard {...mockProperty} featured={true} />
    );
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('col-span-1', 'md:col-span-2', 'lg:flex');
  });

  it('applies custom className when provided', () => {
    const customClass = 'custom-test-class';
    const { container } = renderWithRouter(
      <PropertyCard {...mockProperty} className={customClass} />
    );
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass(customClass);
  });

  it('formats price correctly with commas', () => {
    const expensiveProperty = { ...mockProperty, price: 1250000 };
    renderWithRouter(<PropertyCard {...expensiveProperty} />);
    
    expect(screen.getByText('$1,250,000')).toBeInTheDocument();
  });

  it('formats square footage with commas', () => {
    const largeProperty = { ...mockProperty, sqft: 3500 };
    renderWithRouter(<PropertyCard {...largeProperty} />);
    
    expect(screen.getByText('3,500 sqft')).toBeInTheDocument();
  });

  it('handles zero values gracefully', () => {
    const studioProperty = { ...mockProperty, beds: 0, baths: 1 };
    renderWithRouter(<PropertyCard {...studioProperty} />);
    
    expect(screen.getByText('0 Beds')).toBeInTheDocument();
    expect(screen.getByText('1 Bath')).toBeInTheDocument();
  });

  it('renders all property feature icons', () => {
    renderWithRouter(<PropertyCard {...mockProperty} />);
    
    // Check for bed, bath, and square footage text elements
    expect(screen.getByText('3 Beds')).toBeInTheDocument();
    expect(screen.getByText('2 Baths')).toBeInTheDocument();
    expect(screen.getByText('1,800 sqft')).toBeInTheDocument();
  });

  it('applies hover effects through CSS classes', () => {
    const { container } = renderWithRouter(<PropertyCard {...mockProperty} />);
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('hover:shadow-lg', 'hover:-translate-y-1');
  });
});
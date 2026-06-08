import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { VUMeter } from './VUMeter';

describe('VUMeter', () => {
  it('shows −∞ for silence', () => {
    render(<VUMeter db={-120} />);
    expect(screen.getByText('−∞')).toBeInTheDocument();
  });

  it('rounds and labels a dB value', () => {
    render(<VUMeter db={-6.4} />);
    expect(screen.getByText('-6 dB')).toBeInTheDocument();
  });
});

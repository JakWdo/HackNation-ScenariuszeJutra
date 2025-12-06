/**
 * Deklaracja typów dla react-simple-maps
 */

declare module 'react-simple-maps' {
  import { ComponentType, ReactNode, CSSProperties, MouseEvent } from 'react';

  // Typy dla projekcji
  export type ProjectionFunction = (coordinates: [number, number]) => [number, number] | null;

  // Props dla ComposableMap
  export interface ComposableMapProps {
    projection?: string;
    projectionConfig?: {
      scale?: number;
      center?: [number, number];
      rotate?: [number, number, number];
      parallels?: [number, number];
    };
    width?: number;
    height?: number;
    style?: CSSProperties;
    className?: string;
    children?: ReactNode;
  }

  // Props dla ZoomableGroup
  export interface ZoomableGroupProps {
    center?: [number, number];
    zoom?: number;
    minZoom?: number;
    maxZoom?: number;
    translateExtent?: [[number, number], [number, number]];
    onMoveStart?: (event: { coordinates: [number, number]; zoom: number }) => void;
    onMove?: (event: { coordinates: [number, number]; zoom: number; x: number; y: number; k: number; dragging: boolean }) => void;
    onMoveEnd?: (event: { coordinates: [number, number]; zoom: number }) => void;
    filterZoomEvent?: (event: WheelEvent | TouchEvent) => boolean;
    children?: ReactNode;
  }

  // Obiekt geograficzny
  export interface GeographyObject {
    type: string;
    id: string;
    properties: {
      NAME?: string;
      ISO_A3?: string;
      ISO_A2?: string;
      CONTINENT?: string;
      SUBREGION?: string;
      [key: string]: unknown;
    };
    geometry: {
      type: string;
      coordinates: number[][][] | number[][][][];
    };
    rsmKey: string;
  }

  // Style dla Geography
  export interface GeographyStyleObject {
    default?: CSSProperties;
    hover?: CSSProperties;
    pressed?: CSSProperties;
  }

  // Props dla Geography
  export interface GeographyProps {
    geography: GeographyObject;
    style?: GeographyStyleObject | ((geo: GeographyObject) => GeographyStyleObject);
    className?: string;
    onClick?: (event: MouseEvent<SVGPathElement>) => void;
    onMouseEnter?: (event: MouseEvent<SVGPathElement>) => void;
    onMouseLeave?: (event: MouseEvent<SVGPathElement>) => void;
    onMouseDown?: (event: MouseEvent<SVGPathElement>) => void;
    onMouseUp?: (event: MouseEvent<SVGPathElement>) => void;
    onFocus?: (event: React.FocusEvent<SVGPathElement>) => void;
    onBlur?: (event: React.FocusEvent<SVGPathElement>) => void;
  }

  // Props dla Geographies
  export interface GeographiesProps {
    geography: string | object;
    children: (data: {
      geographies: GeographyObject[];
      outline: GeographyObject;
      borders: GeographyObject;
    }) => ReactNode;
    parseGeographies?: (features: GeographyObject[]) => GeographyObject[];
  }

  // Props dla Marker
  export interface MarkerProps {
    coordinates: [number, number];
    style?: GeographyStyleObject;
    className?: string;
    onClick?: (event: MouseEvent<SVGGElement>) => void;
    onMouseEnter?: (event: MouseEvent<SVGGElement>) => void;
    onMouseLeave?: (event: MouseEvent<SVGGElement>) => void;
    children?: ReactNode;
  }

  // Props dla Line
  export interface LineProps {
    from: [number, number];
    to: [number, number];
    coordinates?: [number, number][];
    stroke?: string;
    strokeWidth?: number;
    strokeLinecap?: 'butt' | 'round' | 'square';
    strokeLinejoin?: 'miter' | 'round' | 'bevel';
    fill?: string;
    className?: string;
    style?: CSSProperties;
  }

  // Props dla Annotation
  export interface AnnotationProps {
    subject: [number, number];
    dx?: number;
    dy?: number;
    curve?: number;
    connectorProps?: object;
    children?: ReactNode;
  }

  // Props dla Sphere
  export interface SphereProps {
    id?: string;
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    className?: string;
    style?: CSSProperties;
  }

  // Props dla Graticule
  export interface GraticuleProps {
    fill?: string;
    stroke?: string;
    strokeWidth?: number;
    step?: [number, number];
    className?: string;
    style?: CSSProperties;
  }

  // Eksporty komponentów
  export const ComposableMap: ComponentType<ComposableMapProps>;
  export const ZoomableGroup: ComponentType<ZoomableGroupProps>;
  export const Geographies: ComponentType<GeographiesProps>;
  export const Geography: ComponentType<GeographyProps>;
  export const Marker: ComponentType<MarkerProps>;
  export const Line: ComponentType<LineProps>;
  export const Annotation: ComponentType<AnnotationProps>;
  export const Sphere: ComponentType<SphereProps>;
  export const Graticule: ComponentType<GraticuleProps>;

  // Funkcje pomocnicze useGeographies
  export function useGeographies(config: { geography: string | object }): {
    geographies: GeographyObject[];
    outline: GeographyObject;
    borders: GeographyObject;
  };
}

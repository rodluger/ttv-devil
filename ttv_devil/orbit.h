/**
@file orbit.h
@brief Main header for the photodynamical routines.
*/
#include <stdio.h>
#include <math.h>

// Constants
#define BIGG                    0.00029591220363                                      /**< Gravitational constant (AU^3 / MSUN / day^2) */
#define PI                      3.14159265358979323846
#define TWOPI                   6.283185307179586476925287

/**
Struct containing all the information pertaining to a
body (star, planet, or moon) in the system.

*/
typedef struct {
  double m;                                                                          /**< Body mass in solar masses */
  double x;                                                                          /**< The Cartesian x position on the sky (right positive) */
  double y;                                                                          /**< The Cartesian y position on the sky (up positive) */
  double z;                                                                          /**< The Cartesian z position on the sky (into sky negative) */
  double vx;                                                                         /**< The Cartesian x velocity on the sky (right positive) */
  double vy;                                                                         /**< The Cartesian y velocity on the sky (up positive) */
  double vz;                                                                         /**< The Cartesian z velocity on the sky (into sky positive) */
  int nt;
  double *transit_times;
} Body;

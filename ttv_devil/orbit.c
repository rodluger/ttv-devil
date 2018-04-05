/**
@file orbit.c
@brief Orbital evolution routines.
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "orbit.h"
#include "rebound.h"


/**
Called at each step of the N-Body simulation. Currently does nothing!

*/
void heartbeat(struct reb_simulation* r){
  // Nothing!
}

/**
Compute the transit times.

*/
void Compute(int np, Body **body, double tstart, double tend, double dt_reb, double dt_trn, double tol, int integrator) {

  int p;
  double t1, t2, t_after, t_before;
  double x_before[np];
  struct reb_simulation* r = reb_create_simulation();

  // Set the timestep
  r->dt = dt_reb;

  // G in AU^3 / MSUN / day^2
  r->G = BIGG;

  // Settings for WHFAST: 11th order symplectic corrector
  r->ri_whfast.safe_mode = 0;
  r->ri_whfast.corrector = 11;
  r->integrator = integrator;
  r->heartbeat = heartbeat;
  r->exact_finish_time = 1;

  // Initialize the particles
  for (p = 0; p < np; p++) {
    struct reb_particle particle = {0};
    particle.x = body[p]->x;
    particle.y = body[p]->y;
    particle.z = body[p]->z;
    particle.vx = body[p]->vx;
    particle.vy = body[p]->vy;
    particle.vz = body[p]->vz;
    particle.m = body[p]->m;
    reb_add(r, particle);
  }

  // Move to center of mass frame
  reb_move_to_com(r);

  // Take steps of size `dt_trn` to search for transits
  while (tstart + r->t < tend) {

      // Get the position of each body relative to the star before the step
      for (p = 1; p < np; p++)
        x_before[p] = r->particles[p].x - r->particles[0].x;

      t1 = r->t;
      reb_integrate(r, r->t + dt_trn);
      reb_integrator_synchronize(r);
      t2 = r->t;

      // Get the position of each body after the step
      for (p = 1; p < np; p++) {

          // Did the x position change sign in front of the star?
          if ((x_before[p] * (r->particles[p].x - r->particles[0].x) < 0) && (r->particles[p].z > 0)) {

              // Bisect until the tolerance is met
              t_before = t1;
              t_after = t2;
              while (t_after - t_before > tol) {
                  if (x_before[p] * (r->particles[p].x - r->particles[0].x) < 0)
                      t_after = r->t;
                  else
                      t_before = r->t;
                  reb_integrate(r, 0.5 * (t_before + t_after));
                  reb_integrator_synchronize(r);
              }

              // Log the transit time
              body[p]->transit_times[body[p]->nt] = tstart + r->t;
              body[p]->nt++;

              // Integrate past the transit
              reb_integrate(r, t_after + dt_trn);

          }

      }

  }

}

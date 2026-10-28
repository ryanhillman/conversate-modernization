// Stands in for RequireProfile, rendering the page without loading a profile.
export const RequireProfile = {
  setup(_, { slots }) {
    return () => slots.default();
  },
};

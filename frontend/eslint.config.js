import js from "@eslint/js";
import prettier from "eslint-config-prettier/flat";
import pluginVue from "eslint-plugin-vue";
import pluginVueA11y from "eslint-plugin-vuejs-accessibility";
import globals from "globals";

export default [
  { ignores: ["dist/**"] },
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  ...pluginVueA11y.configs["flat/recommended"],
  // Last, so Prettier alone decides formatting.
  prettier,
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.browser,
    },
    rules: {
      "no-console": ["error", { allow: ["error", "warn"] }],
      "vue/multi-word-component-names": "off",
      // A label can wrap its field or point to it with for/id; either is valid.
      "vuejs-accessibility/label-has-for": ["error", { required: { some: ["nesting", "id"] } }],
    },
  },
];

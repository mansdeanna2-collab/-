import pluginVue from 'eslint-plugin-vue'
import js from '@eslint/js'
import tseslint from 'typescript-eslint'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue', '**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        requestAnimationFrame: 'readonly',
        Image: 'readonly',
        MediaError: 'readonly',
        Promise: 'readonly',
        Map: 'readonly',
        HTMLImageElement: 'readonly'
      }
    },
    rules: {
      // Vue specific rules - relaxed for existing codebase
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off',
      'vue/require-default-prop': 'off',
      'vue/require-prop-types': 'warn',
      'vue/component-definition-name-casing': ['error', 'PascalCase'],
      'vue/html-indent': ['error', 2],
      'vue/max-attributes-per-line': ['warn', {
        singleline: 5,
        multiline: 1
      }],
      // Turn off formatting rules that are too strict
      'vue/singleline-html-element-content-newline': 'off',
      'vue/html-self-closing': 'off',
      'vue/attributes-order': 'off',
      'vue/order-in-components': 'warn',
      
      // General JavaScript rules
      'no-console': 'off',
      'no-unused-vars': ['warn', { 
        argsIgnorePattern: '^_|^e$|^err$|^error$',
        varsIgnorePattern: '^_'
      }],
      'prefer-const': 'warn',
      'no-var': 'error',
      'eqeqeq': ['warn', 'smart'],
      'curly': ['warn', 'multi-line'],
      'semi': ['warn', 'never'],
      'quotes': ['warn', 'single', { avoidEscape: true }]
    }
  },
  // TypeScript-specific configuration
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: 'module'
      }
    },
    plugins: {
      '@typescript-eslint': tseslint.plugin
    },
    rules: {
      ...tseslint.configs.recommended.rules,
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_'
      }]
    }
  },
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'android/**',
      'ios/**',
      '.capacitor/**'
    ]
  }
]

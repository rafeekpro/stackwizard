/**
 * Error handling utilities for StackWizard CLI
 * Provides comprehensive error handling, logging, and user-friendly messages
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import net from 'net';

const execAsync = promisify(exec);

/**
 * Error codes for different types of failures
 */
export const ErrorCodes = {
  // File system errors
  DIR_EXISTS: 'DIR_EXISTS',
  DIR_CREATE_FAILED: 'DIR_CREATE_FAILED',
  FILE_COPY_FAILED: 'FILE_COPY_FAILED',
  FILE_WRITE_FAILED: 'FILE_WRITE_FAILED',
  FILE_READ_FAILED: 'FILE_READ_FAILED',
  TEMPLATE_NOT_FOUND: 'TEMPLATE_NOT_FOUND',
  TEMPLATE_CORRUPTED: 'TEMPLATE_CORRUPTED',
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  PATH_TOO_LONG: 'PATH_TOO_LONG',

  // Dependency errors
  GIT_NOT_INSTALLED: 'GIT_NOT_INSTALLED',
  GIT_INIT_FAILED: 'GIT_INIT_FAILED',
  NPM_NOT_INSTALLED: 'NPM_NOT_INSTALLED',
  PIP_NOT_INSTALLED: 'PIP_NOT_INSTALLED',
  DOCKER_NOT_INSTALLED: 'DOCKER_NOT_INSTALLED',
  NODE_VERSION_MISMATCH: 'NODE_VERSION_MISMATCH',

  // Network errors
  NPM_INSTALL_FAILED: 'NPM_INSTALL_FAILED',
  PIP_INSTALL_FAILED: 'PIP_INSTALL_FAILED',
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  DNS_ERROR: 'DNS_ERROR',

  // Validation errors
  INVALID_PROJECT_NAME: 'INVALID_PROJECT_NAME',
  INVALID_PORT: 'INVALID_PORT',
  INVALID_DB_CONFIG: 'INVALID_DB_CONFIG',
  PORT_IN_USE: 'PORT_IN_USE',
  RESERVED_NAME: 'RESERVED_NAME',

  // System errors
  OUT_OF_MEMORY: 'OUT_OF_MEMORY',
  DISK_FULL: 'DISK_FULL',
  CPU_OVERLOAD: 'CPU_OVERLOAD',
  SIGNAL_TERMINATED: 'SIGNAL_TERMINATED',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',

  // Process errors
  PROCESS_SPAWN_FAILED: 'PROCESS_SPAWN_FAILED',
  PROCESS_EXIT_ERROR: 'PROCESS_EXIT_ERROR',
  COMMAND_NOT_FOUND: 'COMMAND_NOT_FOUND',
};

/**
 * Custom error class with additional context
 */
export class StackWizardError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.name = 'StackWizardError';
    this.code = code;
    this.details = details;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Error messages with user-friendly explanations and solutions
 */
export const ErrorMessages = {
  [ErrorCodes.DIR_EXISTS]: {
    message: 'Directory already exists',
    solution:
      'Choose a different project name or remove the existing directory',
    recoverable: true,
    autoRecovery: false,
    userAction: ['rename', 'delete', 'overwrite'],
  },
  [ErrorCodes.DIR_CREATE_FAILED]: {
    message: 'Failed to create project directory',
    solution: 'Check if you have write permissions in the current directory',
    recoverable: false,
  },
  [ErrorCodes.FILE_COPY_FAILED]: {
    message: 'Failed to copy template files',
    solution: 'Ensure the StackWizard package is properly installed',
    recoverable: false,
  },
  [ErrorCodes.FILE_WRITE_FAILED]: {
    message: 'Failed to write configuration files',
    solution: 'Check disk space and file permissions',
    recoverable: false,
  },
  [ErrorCodes.TEMPLATE_NOT_FOUND]: {
    message: 'Template files not found',
    solution: 'Reinstall StackWizard: npm install -g @rafeekpro/stackwizard',
    recoverable: false,
  },
  [ErrorCodes.PERMISSION_DENIED]: {
    message: 'Permission denied',
    solution:
      'Run the command with appropriate permissions or choose a different directory',
    recoverable: true,
  },
  [ErrorCodes.GIT_NOT_INSTALLED]: {
    message: 'Git is not installed',
    solution:
      'Install Git from https://git-scm.com/ or skip Git initialization',
    recoverable: true,
  },
  [ErrorCodes.NPM_NOT_INSTALLED]: {
    message: 'npm is not installed',
    solution: 'Install Node.js and npm from https://nodejs.org/',
    recoverable: true,
  },
  [ErrorCodes.PIP_NOT_INSTALLED]: {
    message: 'pip is not installed',
    solution: 'Install Python and pip from https://www.python.org/',
    recoverable: true,
  },
  [ErrorCodes.DOCKER_NOT_INSTALLED]: {
    message: 'Docker is not installed',
    solution: 'Install Docker from https://www.docker.com/get-started',
    recoverable: true,
  },
  [ErrorCodes.NPM_INSTALL_FAILED]: {
    message: 'Failed to install npm dependencies',
    solution: 'Try running "npm install" manually in the frontend directory',
    recoverable: true,
  },
  [ErrorCodes.PIP_INSTALL_FAILED]: {
    message: 'Failed to install Python dependencies',
    solution:
      'Try running "pip install -r requirements.txt" manually in the backend directory',
    recoverable: true,
  },
  [ErrorCodes.NETWORK_ERROR]: {
    message: 'Network connection error',
    solution: 'Check your internet connection and try again',
    recoverable: true,
  },
  [ErrorCodes.INVALID_PROJECT_NAME]: {
    message: 'Invalid project name',
    solution: 'Use only lowercase letters, numbers, and hyphens',
    recoverable: true,
  },
  [ErrorCodes.INVALID_PORT]: {
    message: 'Invalid port number',
    solution: 'Use a port number between 1 and 65535',
    recoverable: true,
  },
  [ErrorCodes.INVALID_DB_CONFIG]: {
    message: 'Invalid database configuration',
    solution: 'Check your database settings and ensure they are valid',
    recoverable: true,
  },
  [ErrorCodes.OUT_OF_MEMORY]: {
    message: 'Out of memory',
    solution: 'Close other applications and try again',
    recoverable: false,
  },
  [ErrorCodes.DISK_FULL]: {
    message: 'Disk is full',
    solution: 'Free up disk space and try again',
    recoverable: false,
  },
  [ErrorCodes.UNKNOWN_ERROR]: {
    message: 'An unexpected error occurred',
    solution:
      'Please report this issue at https://github.com/rafeekpro/stackwizard/issues',
    recoverable: false,
  },
  [ErrorCodes.FILE_READ_FAILED]: {
    message: 'Failed to read file',
    solution: 'Check if the file exists and you have read permissions',
    recoverable: false,
  },
  [ErrorCodes.TEMPLATE_CORRUPTED]: {
    message: 'Template files are corrupted',
    solution: 'Reinstall StackWizard to restore templates',
    recoverable: false,
  },
  [ErrorCodes.PATH_TOO_LONG]: {
    message: 'Path is too long for the operating system',
    solution: 'Use a shorter project name or change to a different directory',
    recoverable: true,
  },
  [ErrorCodes.GIT_INIT_FAILED]: {
    message: 'Failed to initialize Git repository',
    solution: 'Check Git installation and permissions',
    recoverable: true,
  },
  [ErrorCodes.NODE_VERSION_MISMATCH]: {
    message: 'Node.js version requirement not met',
    solution: 'Update Node.js to version 14.0.0 or higher',
    recoverable: false,
  },
  [ErrorCodes.TIMEOUT_ERROR]: {
    message: 'Operation timed out',
    solution: 'Check your internet connection and try again',
    recoverable: true,
  },
  [ErrorCodes.DNS_ERROR]: {
    message: 'DNS resolution failed',
    solution: 'Check your internet connection and DNS settings',
    recoverable: true,
  },
  [ErrorCodes.PORT_IN_USE]: {
    message: 'Port is already in use',
    solution: 'Choose a different port or stop the service using this port',
    recoverable: true,
  },
  [ErrorCodes.RESERVED_NAME]: {
    message: 'Project name is reserved',
    solution: 'Choose a different project name',
    recoverable: true,
  },
  [ErrorCodes.CPU_OVERLOAD]: {
    message: 'System CPU is overloaded',
    solution: 'Close other applications and try again',
    recoverable: true,
  },
  [ErrorCodes.SIGNAL_TERMINATED]: {
    message: 'Process was terminated',
    solution: 'Operation was cancelled',
    recoverable: false,
  },
  [ErrorCodes.PROCESS_SPAWN_FAILED]: {
    message: 'Failed to start process',
    solution: 'Check if the command exists and you have execution permissions',
    recoverable: false,
  },
  [ErrorCodes.PROCESS_EXIT_ERROR]: {
    message: 'Process exited with error',
    solution: 'Check the command output for details',
    recoverable: true,
  },
  [ErrorCodes.COMMAND_NOT_FOUND]: {
    message: 'Command not found',
    solution: 'Install the required tool or check your PATH',
    recoverable: true,
  },
};

/**
 * Logger class for debug mode and error tracking
 */
export class Logger {
  constructor(debugMode = false) {
    this.debugMode = debugMode || process.env.DEBUG === 'true';
    this.logFile = null;
    this.initLogFile();
  }

  initLogFile() {
    if (this.debugMode) {
      const logDir = path.join(os.homedir(), '.stackwizard', 'logs');
      fs.ensureDirSync(logDir);
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      this.logFile = path.join(logDir, `stackwizard-${timestamp}.log`);

      // Clean up old log files (keep last 10)
      this.cleanupOldLogs(logDir);
    }
  }

  cleanupOldLogs(logDir) {
    try {
      const files = fs
        .readdirSync(logDir)
        .filter((f) => f.startsWith('stackwizard-') && f.endsWith('.log'))
        .map((f) => ({
          name: f,
          path: path.join(logDir, f),
          time: fs.statSync(path.join(logDir, f)).mtime,
        }))
        .sort((a, b) => b.time - a.time);

      // Keep only the 10 most recent logs
      if (files.length > 10) {
        files.slice(10).forEach((f) => {
          try {
            fs.unlinkSync(f.path);
          } catch {
            // Ignore cleanup errors
          }
        });
      }
    } catch {
      // Ignore cleanup errors
    }
  }

  debug(message, data = {}) {
    if (this.debugMode) {
      const logEntry = {
        timestamp: new Date().toISOString(),
        level: 'DEBUG',
        message,
        data,
      };

      console.log(chalk.gray(`[DEBUG] ${message}`));
      if (Object.keys(data).length > 0) {
        console.log(chalk.gray(JSON.stringify(data, null, 2)));
      }

      if (this.logFile) {
        fs.appendFileSync(this.logFile, JSON.stringify(logEntry) + '\n');
      }
    }
  }

  info(message) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: 'INFO',
      message,
    };

    if (this.debugMode && this.logFile) {
      fs.appendFileSync(this.logFile, JSON.stringify(logEntry) + '\n');
    }
  }

  warn(message) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: 'WARN',
      message,
    };

    console.log(chalk.yellow(`⚠️  ${message}`));

    if (this.debugMode && this.logFile) {
      fs.appendFileSync(this.logFile, JSON.stringify(logEntry) + '\n');
    }
  }

  error(message, error = null) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: 'ERROR',
      message,
      error: error
        ? {
            message: error.message,
            stack: error.stack,
            code: error.code,
          }
        : null,
    };

    console.log(chalk.red(`❌ ${message}`));

    if (this.debugMode) {
      if (error && error.stack) {
        console.log(chalk.red(error.stack));
      }
      if (this.logFile) {
        fs.appendFileSync(this.logFile, JSON.stringify(logEntry) + '\n');
      }
    }
  }

  getLogPath() {
    return this.logFile;
  }
}

/**
 * Error handler with recovery mechanisms
 */
export class ErrorHandler {
  constructor(logger) {
    this.logger = logger;
    this.errorCount = 0;
    this.recoveryAttempts = {};
  }

  /**
   * Handle error with appropriate user messaging and recovery
   */
  async handle(error, context = {}) {
    this.errorCount++;
    this.logger.error(`Error #${this.errorCount}: ${error.message}`, error);

    // Capture error context for better debugging
    const errorContext = {
      ...context,
      timestamp: new Date().toISOString(),
      platform: process.platform,
      nodeVersion: process.version,
      cwd: process.cwd(),
      memoryUsage: process.memoryUsage(),
      cpuUsage: process.cpuUsage(),
    };

    this.logger.debug('Error context', errorContext);

    // Determine error code
    const errorCode = this.determineErrorCode(error);
    const errorInfo =
      ErrorMessages[errorCode] || ErrorMessages[ErrorCodes.UNKNOWN_ERROR];

    // Display user-friendly error message
    console.log('\n' + chalk.red.bold('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'));
    console.log(chalk.red.bold('  🚨 Error Occurred'));
    console.log(chalk.red.bold('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'));

    console.log(chalk.white(`\n  ${chalk.bold('What happened:')}`));
    console.log(chalk.white(`  ${errorInfo.message}`));

    if (context.details) {
      console.log(chalk.white(`\n  ${chalk.bold('Details:')}`));
      console.log(chalk.gray(`  ${context.details}`));
    }

    console.log(chalk.white(`\n  ${chalk.bold('How to fix:')}`));
    console.log(chalk.cyan(`  ${errorInfo.solution}`));

    if (this.logger.debugMode) {
      console.log(chalk.white(`\n  ${chalk.bold('Debug Information:')}`));
      console.log(chalk.gray(`  Error Code: ${errorCode}`));
      console.log(chalk.gray(`  Log File: ${this.logger.getLogPath()}`));
    }

    console.log(chalk.red.bold('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'));

    // Attempt recovery if possible
    if (errorInfo.recoverable) {
      return await this.attemptRecovery(errorCode, error, context);
    }

    return false;
  }

  /**
   * Determine error code from error object
   */
  determineErrorCode(error) {
    if (error instanceof StackWizardError) {
      return error.code;
    }

    // Check error code if present
    if (error.code) {
      const codeMap = {
        EEXIST: ErrorCodes.DIR_EXISTS,
        ENOENT: ErrorCodes.TEMPLATE_NOT_FOUND,
        EACCES: ErrorCodes.PERMISSION_DENIED,
        EPERM: ErrorCodes.PERMISSION_DENIED,
        ENOSPC: ErrorCodes.DISK_FULL,
        ENOMEM: ErrorCodes.OUT_OF_MEMORY,
        ETIMEDOUT: ErrorCodes.TIMEOUT_ERROR,
        ENOTFOUND: ErrorCodes.DNS_ERROR,
        EADDRINUSE: ErrorCodes.PORT_IN_USE,
        ENAMETOOLONG: ErrorCodes.PATH_TOO_LONG,
      };

      if (codeMap[error.code]) {
        return codeMap[error.code];
      }
    }

    // Check for common error patterns
    const message = error.message.toLowerCase();

    if (message.includes('eexist')) return ErrorCodes.DIR_EXISTS;
    if (message.includes('eacces') || message.includes('permission'))
      return ErrorCodes.PERMISSION_DENIED;
    if (message.includes('enoent')) return ErrorCodes.TEMPLATE_NOT_FOUND;
    if (message.includes('enospc')) return ErrorCodes.DISK_FULL;
    if (message.includes('enomem')) return ErrorCodes.OUT_OF_MEMORY;
    if (message.includes('git')) return ErrorCodes.GIT_NOT_INSTALLED;
    if (message.includes('npm')) return ErrorCodes.NPM_INSTALL_FAILED;
    if (message.includes('pip')) return ErrorCodes.PIP_INSTALL_FAILED;
    if (message.includes('network') || message.includes('enotfound'))
      return ErrorCodes.NETWORK_ERROR;

    return ErrorCodes.UNKNOWN_ERROR;
  }

  /**
   * Attempt to recover from recoverable errors
   */
  async attemptRecovery(errorCode, error, context) {
    const recoveryKey = `${errorCode}_${context.projectName || 'default'}`;

    if (!this.recoveryAttempts[recoveryKey]) {
      this.recoveryAttempts[recoveryKey] = 0;
    }

    this.recoveryAttempts[recoveryKey]++;

    if (this.recoveryAttempts[recoveryKey] > 3) {
      this.logger.warn('Maximum recovery attempts reached');
      return false;
    }

    this.logger.info(
      `Attempting recovery (attempt ${this.recoveryAttempts[recoveryKey]}/3)`
    );

    switch (errorCode) {
      case ErrorCodes.DIR_EXISTS:
        return await this.recoverFromDirExists(context);

      case ErrorCodes.GIT_NOT_INSTALLED:
      case ErrorCodes.NPM_NOT_INSTALLED:
      case ErrorCodes.PIP_NOT_INSTALLED:
        return await this.recoverFromMissingDependency(errorCode, context);

      case ErrorCodes.NETWORK_ERROR:
        return await this.recoverFromNetworkError(context);

      default:
        return false;
    }
  }

  /**
   * Recovery strategies for specific error types
   */
  async recoverFromDirExists() {
    console.log(chalk.yellow('\n💡 Recovery Options:'));
    console.log(chalk.white('  1. Choose a different project name'));
    console.log(chalk.white('  2. Remove the existing directory'));
    console.log(chalk.white('  3. Cancel the operation\n'));

    // Return true to indicate recovery options were presented
    return true;
  }

  async recoverFromMissingDependency(errorCode, context) {
    console.log(chalk.yellow('\n💡 Continuing without this feature...'));

    // Mark the feature as skipped
    if (context.skipFeatures) {
      context.skipFeatures.push(errorCode);
    }

    return true;
  }

  async recoverFromNetworkError() {
    console.log(chalk.yellow('\n💡 Network issue detected'));
    console.log(chalk.white('  You can install dependencies manually later:'));
    console.log(
      chalk.gray('  • Backend: cd backend && pip install -r requirements.txt')
    );
    console.log(chalk.gray('  • Frontend: cd frontend && npm install\n'));

    return true;
  }

  /**
   * Generate error report for debugging
   */
  generateErrorReport() {
    const report = {
      timestamp: new Date().toISOString(),
      platform: process.platform,
      nodeVersion: process.version,
      stackwizardVersion: process.env.npm_package_version || 'unknown',
      errorCount: this.errorCount,
      logFile: this.logger.getLogPath(),
    };

    if (this.logger.debugMode) {
      const reportPath = path.join(
        os.homedir(),
        '.stackwizard',
        'error-report.json'
      );
      fs.writeJsonSync(reportPath, report, { spaces: 2 });
      console.log(chalk.gray(`\nError report saved to: ${reportPath}`));
    }

    return report;
  }
}

/**
 * Input validators with detailed error messages
 */
export const Validators = {
  projectName: (input) => {
    if (!input || input.trim() === '') {
      return 'Project name cannot be empty';
    }

    if (!/^[a-z0-9-]+$/.test(input)) {
      return 'Project name can only contain lowercase letters, numbers, and hyphens';
    }

    if (input.startsWith('-') || input.endsWith('-')) {
      return 'Project name cannot start or end with a hyphen';
    }

    if (input.length > 50) {
      return 'Project name is too long (max 50 characters)';
    }

    // Check for reserved names
    const reserved = [
      'node_modules',
      'dist',
      'build',
      'test',
      'tests',
      '.git',
      '.env',
      'src',
      'lib',
      'bin',
    ];
    if (reserved.includes(input.toLowerCase())) {
      return `"${input}" is a reserved name. Please choose another`;
    }

    // Check for npm package naming conventions
    if (input.includes('--')) {
      return 'Project name cannot contain consecutive hyphens';
    }

    return true;
  },

  port: (input) => {
    const port = parseInt(input);

    if (isNaN(port)) {
      return 'Port must be a number';
    }

    if (port < 1 || port > 65535) {
      return 'Port must be between 1 and 65535';
    }

    // Check for commonly used ports
    const commonPorts = [80, 443, 22, 21, 25, 3306, 5432, 27017];
    if (commonPorts.includes(port)) {
      return `Port ${port} is commonly used by other services. Consider using a different port`;
    }

    return true;
  },

  databaseName: (input) => {
    if (!input || input.trim() === '') {
      return 'Database name cannot be empty';
    }

    if (!/^[a-z0-9_]+$/.test(input)) {
      return 'Database name can only contain lowercase letters, numbers, and underscores';
    }

    if (input.startsWith('_') || input.endsWith('_')) {
      return 'Database name cannot start or end with an underscore';
    }

    return true;
  },

  databaseUser: (input) => {
    if (!input || input.trim() === '') {
      return 'Database user cannot be empty';
    }

    if (!/^[a-zA-Z0-9_]+$/.test(input)) {
      return 'Database user can only contain letters, numbers, and underscores';
    }

    return true;
  },

  databasePassword: (input) => {
    if (!input || input.trim() === '') {
      return 'Database password cannot be empty';
    }

    if (input.length < 8) {
      return 'Password should be at least 8 characters long for security';
    }

    return true;
  },
};

/**
 * Check system requirements
 */
export async function checkSystemRequirements(logger) {
  const requirements = {
    node: {
      command: 'node --version',
      name: 'Node.js',
      optional: false,
      minVersion: '14.0.0',
    },
    npm: {
      command: 'npm --version',
      name: 'npm',
      optional: false,
      minVersion: '6.0.0',
    },
    git: { command: 'git --version', name: 'Git', optional: true },
    docker: { command: 'docker --version', name: 'Docker', optional: true },
    python: {
      command: 'python3 --version || python --version',
      name: 'Python',
      optional: true,
      minVersion: '3.8.0',
    },
    pip: {
      command: 'pip3 --version || pip --version',
      name: 'pip',
      optional: true,
    },
  };

  const results = {};

  for (const [key, req] of Object.entries(requirements)) {
    try {
      const { stdout } = await execAsync(req.command);
      const version = extractVersion(stdout);

      results[key] = {
        installed: true,
        name: req.name,
        version,
        optional: req.optional,
      };

      // Check minimum version if specified
      if (req.minVersion && version) {
        const meetsRequirement = compareVersions(version, req.minVersion) >= 0;
        if (!meetsRequirement && !req.optional) {
          throw new StackWizardError(
            ErrorCodes.NODE_VERSION_MISMATCH,
            `${req.name} version ${req.minVersion} or higher is required (found: ${version})`
          );
        }
        results[key].meetsRequirement = meetsRequirement;
      }

      logger.debug(`${req.name} is installed (version: ${version})`);
    } catch (error) {
      if (error instanceof StackWizardError) {
        throw error;
      }
      results[key] = {
        installed: false,
        name: req.name,
        optional: req.optional,
        version: null,
      };

      if (!req.optional) {
        throw new StackWizardError(
          ErrorCodes[`${key.toUpperCase()}_NOT_INSTALLED`] ||
            ErrorCodes.COMMAND_NOT_FOUND,
          `${req.name} is required but not installed`
        );
      } else {
        logger.warn(`${req.name} is not installed (optional)`);
      }
    }
  }

  return results;
}

/**
 * Clean up on error
 */
export async function cleanup(projectPath, logger) {
  if (projectPath && fs.existsSync(projectPath)) {
    try {
      logger.info(`Cleaning up incomplete project at ${projectPath}`);

      // Create backup before cleanup if project has substantial content
      const stats = await fs.stat(projectPath);
      if (stats.size > 1024 * 1024) {
        // If > 1MB, create backup
        const backupPath = `${projectPath}.backup-${Date.now()}`;
        logger.info(`Creating backup at ${backupPath}`);
        await fs.copy(projectPath, backupPath);
        console.log(chalk.yellow(`Backup created at: ${backupPath}`));
      }

      await fs.remove(projectPath);
      console.log(chalk.yellow('✓ Cleaned up incomplete project files'));
    } catch (error) {
      logger.error('Failed to clean up project files', error);
      console.log(
        chalk.red(
          '⚠️  Failed to clean up. Please manually remove: ' + projectPath
        )
      );
    }
  }
}

/**
 * Extract version from command output
 */
function extractVersion(output) {
  const versionMatch = output.match(/(\d+\.\d+\.\d+)/);
  return versionMatch ? versionMatch[1] : null;
}

/**
 * Compare semantic versions
 */
function compareVersions(current, required) {
  const currentParts = current.split('.').map(Number);
  const requiredParts = required.split('.').map(Number);

  for (
    let i = 0;
    i < Math.max(currentParts.length, requiredParts.length);
    i++
  ) {
    const currentPart = currentParts[i] || 0;
    const requiredPart = requiredParts[i] || 0;

    if (currentPart > requiredPart) return 1;
    if (currentPart < requiredPart) return -1;
  }

  return 0;
}

/**
 * Check if port is available
 */
export async function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();

    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(false);
      } else {
        resolve(false);
      }
    });

    server.once('listening', () => {
      server.close();
      resolve(true);
    });

    server.listen(port, '127.0.0.1');
  });
}

/**
 * Get system information for debugging
 */
export function getSystemInfo() {
  return {
    platform: process.platform,
    arch: process.arch,
    nodeVersion: process.version,
    npmVersion: process.env.npm_version || 'unknown',
    memory: {
      total: os.totalmem(),
      free: os.freemem(),
      used: process.memoryUsage(),
    },
    cpu: {
      cores: os.cpus().length,
      model: os.cpus()[0]?.model || 'unknown',
      usage: process.cpuUsage(),
    },
    user: os.userInfo(),
    cwd: process.cwd(),
    env: {
      PATH: process.env.PATH,
      NODE_ENV: process.env.NODE_ENV,
      DEBUG: process.env.DEBUG,
    },
  };
}

/**
 * Format bytes to human readable size
 */
export function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Create error context for debugging
 */
export function createErrorContext(error, additionalContext = {}) {
  return {
    error: {
      name: error.name,
      message: error.message,
      code: error.code,
      stack: error.stack,
    },
    system: getSystemInfo(),
    context: additionalContext,
    timestamp: new Date().toISOString(),
  };
}

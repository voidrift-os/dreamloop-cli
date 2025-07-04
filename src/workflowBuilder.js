const logger = require('./logger');

class WorkflowBuilder {
  constructor(eventBus) {
    this.eventBus = eventBus;
    this.workflows = new Map();
  }

  createWorkflow(name) {
    const workflow = { name, steps: [], conditions: new Map(), compensations: new Map() };
    const builder = {
      addStep: (stepName, handler, options = {}) => {
        workflow.steps.push({ name: stepName, handler, timeout: options.timeout || 30000, compensate: options.compensate });
        return builder;
      },
      addCondition: (stepName, condition) => { workflow.conditions.set(stepName, condition); return builder; },
      addCompensation: (stepName, compensation) => { workflow.compensations.set(stepName, compensation); return builder; },
      build: () => { this.workflows.set(name, workflow); return workflow; }
    };
    return builder;
  }

  async executeWorkflow(workflowName, context) {
    const workflow = this.workflows.get(workflowName);
    if (!workflow) throw new Error(`Workflow ${workflowName} not found`);
    const execId = `exec_${Date.now()}`;
    const execCtx = { ...context, executionId: execId, completedSteps: [], results: new Map() };
    logger.info('Starting workflow', { workflowName, executionId: execId });
    try {
      for (const step of workflow.steps) {
        const cond = workflow.conditions.get(step.name);
        if (cond && !cond(execCtx)) {
          logger.info('Skipping step', { step: step.name });
          continue;
        }
        const result = await this.executeStep(step, execCtx);
        execCtx.results.set(step.name, result);
        execCtx.completedSteps.push(step.name);
      }
      return Object.fromEntries(execCtx.results);
    } catch (err) {
      logger.error('Workflow failed', { workflowName, error: err.message });
      await this.runCompensations(workflow, execCtx);
      throw err;
    }
  }

  async executeStep(step, context) {
    const start = Date.now();
    let timeoutHandle;
    const timeoutPromise = new Promise((_, reject) => {
      timeoutHandle = setTimeout(() => reject(new Error('Step timeout')), step.timeout);
    });
    try {
      const result = await Promise.race([step.handler(context), timeoutPromise]);
      clearTimeout(timeoutHandle);
      logger.info('Step executed', { step: step.name, duration: Date.now() - start });
      return result;
    } catch (err) {
      logger.warn('Step failed', { step: step.name, error: err.message });
      throw err;
    }
  }

  async runCompensations(workflow, ctx) {
    for (const stepName of [...ctx.completedSteps].reverse()) {
      const comp = workflow.compensations.get(stepName);
      if (comp) {
        try {
          await comp(ctx);
          logger.info('Compensation executed', { step: stepName });
        } catch (err) {
          logger.error('Compensation failed', { step: stepName, error: err.message });
        }
      }
    }
  }
}

module.exports = WorkflowBuilder;

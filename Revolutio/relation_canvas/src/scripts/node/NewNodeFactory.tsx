import * as React from 'react';
import { NewNodeModel } from './NewNodeModel';
import { NewNodeWidget } from './NewNodeWidget';
import { AbstractReactFactory } from '@projectstorm/react-canvas-core';
import { DiagramEngine } from '@projectstorm/react-diagrams-core';

export class NewNodeFactory extends AbstractReactFactory<NewNodeModel, DiagramEngine> {
	constructor() {
		super('default');
	}

	generateReactWidget(event): JSX.Element {
		return <NewNodeWidget engine={this.engine} node={event.model} />;
	}

	generateModel(event): NewNodeModel {
		return new NewNodeModel();
	}
}

import * as React from 'react';
import { SimpleNodeModel } from './SimpleNodeModel';
import { SimpleNodeWidget } from './SimpleNodeWidget';
import { AbstractReactFactory } from '@projectstorm/react-canvas-core';
import { DiagramEngine } from '@projectstorm/react-diagrams-core';

export class SimpleNodeFactory extends AbstractReactFactory<SimpleNodeModel, DiagramEngine> {
	constructor() {
		super('default');
	}

	generateReactWidget(event): JSX.Element {
		return <SimpleNodeWidget engine={this.engine} node={event.model} />;
	}

	generateModel(event): SimpleNodeModel {
		return new SimpleNodeModel();
	}
}

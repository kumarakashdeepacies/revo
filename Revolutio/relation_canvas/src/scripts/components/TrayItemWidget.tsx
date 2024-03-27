import * as React from 'react';
import styled from '@emotion/styled';
import ReactTooltip from 'react-tooltip';

export interface TrayItemWidgetProps {
	color?: string;
	tooltip?: string,
	name: string;
}

namespace S {
	export const Tray = styled.div<{ color: string }>`
		color: #495057;
		font-family: Arial;
		padding: 5px;
		margin: 0px 10px;
		border: 1px solid rgba(0,0,0,.125);
		// border-radius: 5px;
		// margin-bottom: 2px;
		cursor: pointer;
	`;
}

export class TrayItemWidget extends React.Component<TrayItemWidgetProps> {
	render() {
		return (
			<React.Fragment>
				<S.Tray
					color={this.props.color}
					data-for={this.props.name}
					data-tip={this.props.tooltip}
					draggable={true}
					onDragStart={event => {
						event.dataTransfer.setData('storm-diagram-node', JSON.stringify(this.props.name));
					}}
					className="tray-item">
					{this.props.name}
				</S.Tray>
				<ReactTooltip id={this.props.name} place="right" multiline={true} />
			</React.Fragment>
		);
	}
}

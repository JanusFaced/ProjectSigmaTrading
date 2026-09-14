import React from 'react';
import { 
    ModalOverlay,
    ModalContent,
    ModalHeader,
    CloseButton,
    ModalBody,
    InfoBox,
    WarningText,
    ModalFooter,
    CancelButton,
    ConfirmButton,
} from './DeleteModal.styles.jsx';

const DeleteModal = ({ show, onClose, onConfirm, name, details, type }) => {
    if (!show) return null;

    return (
        <ModalOverlay show={show} onClick={onClose}>
            <ModalContent onClick={(e) => e.stopPropagation()}>
                <ModalHeader>
                    <h3>⚠️ Deletion confirmation</h3>
                    <CloseButton onClick={onClose}>×</CloseButton>
                </ModalHeader>
                <ModalBody>
                    <p>Do you really want to delete <strong>forever</strong>:</p>
                    <InfoBox>
                        <strong>{name}</strong>
                        <div className="detail">{details}</div>
                    </InfoBox>
                    <WarningText>
                        ⚠️ This action is <strong>irreversible</strong>! 
                        {type === 'signal' && ' All related trades will be deleted.'}
                    </WarningText>
                </ModalBody>
                <ModalFooter>
                    <CancelButton onClick={onClose}>Cancel</CancelButton>
                    <ConfirmButton onClick={onConfirm}>
                        🗑️ Yes, delete
                    </ConfirmButton>
                </ModalFooter>
            </ModalContent>
        </ModalOverlay>
    );
};

export default DeleteModal;
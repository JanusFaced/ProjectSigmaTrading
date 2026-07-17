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
                    <h3>⚠️ Подтверждение удаления</h3>
                    <CloseButton onClick={onClose}>×</CloseButton>
                </ModalHeader>
                <ModalBody>
                    <p>Вы действительно хотите <strong>навсегда</strong> удалить:</p>
                    <InfoBox>
                        <strong>{name}</strong>
                        <div className="detail">{details}</div>
                    </InfoBox>
                    <WarningText>
                        ⚠️ Это действие <strong>необратимо</strong>! 
                        {type === 'signal' && ' Все связанные трейды будут удалены.'}
                    </WarningText>
                </ModalBody>
                <ModalFooter>
                    <CancelButton onClick={onClose}>Отмена</CancelButton>
                    <ConfirmButton onClick={onConfirm}>
                        🗑️ Да, удалить
                    </ConfirmButton>
                </ModalFooter>
            </ModalContent>
        </ModalOverlay>
    );
};

export default DeleteModal;